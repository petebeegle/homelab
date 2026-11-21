"""base_smoke: apply a PR to the development cluster's own platform, check it, always restore."""
from __future__ import annotations

import json
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import base_smoke  # noqa: E402

SHA = "0123456789abcdef0123456789abcdef01234567"
CHILDREN = """\
apiVersion: kustomize.toolkit.fluxcd.io/v1
kind: Kustomization
metadata:
  name: cilium
  namespace: flux-system
spec:
  path: ./kubernetes/infra/network/cilium
  sourceRef:
    kind: GitRepository
    name: flux-system
---
apiVersion: kustomize.toolkit.fluxcd.io/v1
kind: Kustomization
metadata:
  name: app-whoami
  namespace: flux-system
spec:
  path: ./kubernetes/apps/whoami
  sourceRef:
    kind: GitRepository
    name: flux-system
"""


def ks(name: str, *, ready: bool = True, source: str = "flux-system", revision: str = "main@sha1:aaaa") -> dict:
    return {
        "metadata": {"name": name},
        "spec": {"sourceRef": {"kind": "GitRepository", "name": source}},
        "status": {
            "lastAppliedRevision": revision,
            "conditions": [{"type": "Ready", "status": "True" if ready else "False", "message": "m"}],
        },
    }


class FakeCluster:
    """Answers the commands base_smoke runs, and records them."""

    def __init__(self, *, test_ready: bool = True, canary_ok: bool = True, recovers: bool = True) -> None:
        self.commands: list[str] = []
        self.inputs: list[str] = []
        self.phase = "before"
        self.test_ready = test_ready
        self.canary_ok = canary_ok
        self.recovers = recovers
        self.quiet = True

    def kustomizations(self) -> list[dict]:
        if self.phase == "before":
            return [ks("flux-system"), ks("cilium"), ks("app-whoami")]
        if self.phase == "testing":
            rev = f"base-pr-7@sha1:{SHA}"
            return [
                ks("flux-system"),
                ks("cilium", source="base-pr-7", revision=rev, ready=self.test_ready),
                ks("app-whoami", source="base-pr-7", revision=rev),
                ks("new-from-pr", source="base-pr-7", revision=rev),
            ]
        # restored: root re-applied main's children; the PR-only child still points at base-pr-7
        return [ks("flux-system"), ks("cilium", ready=self.recovers), ks("app-whoami"), ks("new-from-pr", source="base-pr-7")]

    def __call__(self, args, input=None, **_):
        line = " ".join(args)
        self.commands.append(line)
        if input:
            self.inputs.append(input)
        out, rc = "", 0
        if "get kustomizations.kustomize.toolkit.fluxcd.io" in line:
            out = json.dumps({"items": self.kustomizations()})
        elif "get helmreleases.helm.toolkit.fluxcd.io" in line:
            out = json.dumps({"items": []})
        elif "get gitrepository.source.toolkit.fluxcd.io/flux-system" in line:
            out = json.dumps({"spec": {"url": "ssh://git@github.com/o/r", "secretRef": {"name": "flux-system"}, "ref": {"branch": "main"}}})
        elif line.startswith("kubectl kustomize"):
            out = CHILDREN
        elif "apply --server-side" in line and input and "kind: Kustomization" in input:
            self.phase = "testing"
        elif "resume kustomization flux-system" in line:
            self.phase = "restored"
        elif "verify_branch_deploy.py" in line:
            rc = 0 if self.canary_ok else 1
        return SimpleNamespace(returncode=rc, stdout=out, stderr="")


def config(head: Path) -> base_smoke.Config:
    return base_smoke.Config(
        kubeconfig=Path("/kc"), pr=7, sha=SHA, head_dir=head,
        base_dir=Path("."), ready_timeout_s=60, poll_s=1, canaries=("whoami",),
    )


class BaseSmokeTest(unittest.TestCase):
    def run_smoke(self, cluster: FakeCluster) -> int:
        head = Path(tempfile.mkdtemp())
        return base_smoke.run(config(head), runner=cluster, sleep=lambda _s: None, clock=iter(range(0, 10_000, 5)).__next__)

    def index(self, cluster: FakeCluster, needle: str) -> int:
        return next(i for i, c in enumerate(cluster.commands) if needle in c)

    def test_passes_and_restores(self) -> None:
        cluster = FakeCluster()
        self.assertEqual(self.run_smoke(cluster), 0)
        order = [
            "annotate kustomization flux-system homelab.dev/base-smoke=pr-7",
            "suspend kustomization flux-system",
            "verify_branch_deploy.py",
            "resume kustomization flux-system",
            "delete gitrepository.source.toolkit.fluxcd.io/base-pr-7",
        ]
        positions = [self.index(cluster, step) for step in order]
        self.assertEqual(positions, sorted(positions), cluster.commands)

    def test_source_is_flux_systems_repo_at_the_prs_merge_onto_main(self) -> None:
        cluster = FakeCluster()
        self.run_smoke(cluster)
        source = json.loads(next(i for i in cluster.inputs if '"GitRepository"' in i))
        self.assertEqual(source["metadata"]["name"], "base-pr-7")
        self.assertEqual(source["spec"]["url"], "ssh://git@github.com/o/r")
        self.assertEqual(source["spec"]["secretRef"], {"name": "flux-system"})
        # The PR as it would land: GitHub's test merge onto main, never the (possibly stale) head.
        self.assertEqual(source["spec"]["ref"], {"name": "refs/pull/7/merge"})
        self.assertEqual(source["spec"]["interval"], "60m", "must not refetch a moved merge ref mid-test")

    def test_only_child_kustomizations_are_repointed(self) -> None:
        cluster = FakeCluster()
        self.run_smoke(cluster)
        applied = next(i for i in cluster.inputs if "kind: Kustomization" in i)
        self.assertEqual(applied.count("name: base-pr-7"), 2)
        self.assertNotIn("name: flux-system\n  namespace", applied.replace("  namespace: flux-system", ""))
        self.assertTrue(any("kustomize" in c and "clusters/development/infra" in c for c in cluster.commands))
        self.assertTrue(any("kustomize" in c and "clusters/development/apps" in c for c in cluster.commands))

    def test_kustomizations_only_the_pr_created_are_deleted_on_restore(self) -> None:
        cluster = FakeCluster()
        self.run_smoke(cluster)
        self.assertTrue(any("delete kustomization.kustomize.toolkit.fluxcd.io new-from-pr" in c for c in cluster.commands))
        self.assertFalse(any("delete kustomization.kustomize.toolkit.fluxcd.io cilium" in c for c in cluster.commands))

    def test_a_platform_that_never_settles_fails_but_still_restores(self) -> None:
        cluster = FakeCluster(test_ready=False)
        self.assertEqual(self.run_smoke(cluster), 1)
        self.assertFalse(any("verify_branch_deploy.py" in c for c in cluster.commands), "no canary on a broken base")
        self.assertTrue(any("resume kustomization flux-system" in c for c in cluster.commands))

    def test_canaries_deploy_known_good_apps_from_main(self) -> None:
        cluster = FakeCluster()
        self.run_smoke(cluster)
        canary = next(c for c in cluster.commands if "verify_branch_deploy.py" in c)
        self.assertIn("--branch main", canary)

    def test_a_failed_canary_fails_but_still_restores(self) -> None:
        cluster = FakeCluster(canary_ok=False)
        self.assertEqual(self.run_smoke(cluster), 1)
        self.assertTrue(any("resume kustomization flux-system" in c for c in cluster.commands))
        self.assertTrue(any("cleanup_pr_envs.py" in c and "pr-7" in c for c in cluster.commands))

    def test_a_development_that_does_not_recover_is_its_own_failure(self) -> None:
        cluster = FakeCluster(recovers=False)
        self.assertEqual(self.run_smoke(cluster), 2)

    def test_refuses_to_start_on_an_unhealthy_development(self) -> None:
        cluster = FakeCluster()
        cluster.kustomizations = lambda: [ks("flux-system"), ks("cilium", ready=False)]  # type: ignore[method-assign]
        self.assertEqual(self.run_smoke(cluster), 1)
        self.assertFalse(any("suspend" in c for c in cluster.commands), "must not touch an unhealthy development")


class RecoverStaleTest(unittest.TestCase):
    """The sweep's safety net: a job killed mid-test leaves the root suspended and stamped."""

    def cluster_with_root(self, annotations: dict, suspended: bool = True) -> FakeCluster:
        cluster = FakeCluster()
        cluster.phase = "testing"
        original = cluster.__call__

        def call(args, input=None, **kw):
            line = " ".join(args)
            if "get kustomization.kustomize.toolkit.fluxcd.io/flux-system" in line:
                cluster.commands.append(line)
                root = {"metadata": {"name": "flux-system", "annotations": annotations}, "spec": {"suspend": suspended}}
                return SimpleNamespace(returncode=0, stdout=json.dumps(root), stderr="")
            return original(args, input=input, **kw)

        cluster.call = call  # type: ignore[attr-defined]
        return cluster

    def recover(self, cluster: FakeCluster, now: float) -> int:
        return base_smoke.recover_stale(
            Path("/kc"), max_age_s=3600, runner=cluster.call, now=now, sleep=lambda _s: None,
            clock=iter(range(0, 10_000, 5)).__next__,
        )

    def test_restores_a_root_stamped_more_than_an_hour_ago(self) -> None:
        cluster = self.cluster_with_root({"homelab.dev/base-smoke": "pr-7", "homelab.dev/suspended-at": "1000"})
        self.assertEqual(self.recover(cluster, now=1000 + 3601), 0)
        self.assertTrue(any("resume kustomization flux-system" in c for c in cluster.commands))
        self.assertTrue(any("delete gitrepository.source.toolkit.fluxcd.io/base-pr-7" in c for c in cluster.commands))

    def test_leaves_a_running_test_alone(self) -> None:
        cluster = self.cluster_with_root({"homelab.dev/base-smoke": "pr-7", "homelab.dev/suspended-at": "1000"})
        self.assertEqual(self.recover(cluster, now=1000 + 600), 0)
        self.assertFalse(any("resume" in c for c in cluster.commands))

    def test_leaves_a_root_a_person_suspended_alone(self) -> None:
        cluster = self.cluster_with_root({})
        self.assertEqual(self.recover(cluster, now=10_000_000), 0)
        self.assertFalse(any("resume" in c for c in cluster.commands))


if __name__ == "__main__":
    unittest.main()
