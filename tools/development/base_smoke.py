#!/usr/bin/env python3
"""Apply a PR to the development cluster's own platform, check it, and always restore.

Used by dev-smoke's `base` job for PRs that change something development runs
(tools/development/affected_dev.py decides). It runs on the production runner, so a
PR that breaks development's networking cannot take the restore down with it.

1. Refuse to start unless every development Flux Kustomization is Ready.
2. Stamp and suspend the root `flux-system` Kustomization. The root re-applies every
   child's spec, so it would undo step 4 while it runs.
3. Create GitRepository `base-pr-<N>`: flux-system's repository and deploy key at
   branch `base-smoke/pr-<N>`, on which the workflow merges the PR onto current main
   (.github/actions/pr-merge) and which it always deletes.
   Never the PR head: a branch behind main would roll development back. `--sha` is
   that merge commit.
4. Render the PR's kubernetes/clusters/development/{infra,apps} (data only) and apply
   every child Kustomization with its sourceRef pointed at `base-pr-<N>`.
5. Wait until every Kustomization from the PR has applied that commit and is Ready,
   and every HelmRelease is Ready.
6. Canaries: the whoami and homepage smoke tests, deployed from main (known-good apps)
   onto the changed platform, through its Gateway, TLS and (whoami) the browser check.
   Development's own whoami and homepage already run the PR's version via step 4.
7. Always: resume the root, which re-applies main's children; delete Kustomizations
   only the PR created; delete the source; wait until development is Ready again.

Exit 0: passed and restored. 1: the PR failed (development restored). 2: development
did not recover. The `homelab.dev/suspended-at` stamp lets the stale sweep resume a
root that a killed job left suspended.
"""

from __future__ import annotations

import argparse
import json
import shlex
import signal
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterable, Sequence

from devverify.summary import Stages, append, step_summary_path

NS = "flux-system"
KS = "kustomization.kustomize.toolkit.fluxcd.io"
KS_LIST = "kustomizations.kustomize.toolkit.fluxcd.io"
GITREPO = "gitrepository.source.toolkit.fluxcd.io"
HR_LIST = "helmreleases.helm.toolkit.fluxcd.io"
CLUSTER = Path("kubernetes/clusters/development")
STAMP = "homelab.dev/base-smoke"
STAMP_TIME = "homelab.dev/suspended-at"
SOURCE_REF = "  sourceRef:\n    kind: GitRepository\n    name: flux-system\n"
BROWSER_CANARIES = ("whoami",)


class Failure(RuntimeError):
    pass


@dataclass(frozen=True)
class Config:
    kubeconfig: Path
    pr: int
    sha: str
    head_dir: Path
    base_dir: Path
    ready_timeout_s: int = 1200
    poll_s: int = 15
    canaries: tuple[str, ...] = ("whoami", "homepage")
    step_summary: Path | None = None

    @property
    def source(self) -> str:
        return f"base-pr-{self.pr}"

    @property
    def slug(self) -> str:
        return f"pr-{self.pr}"


Runner = Callable[..., object]


class Cluster:
    def __init__(self, config: Config, runner: Runner, sleep: Callable[[float], None], clock: Callable[[], float]):
        self.c, self.runner, self.sleep, self.clock = config, runner, sleep, clock

    def run(self, args: Sequence[str], *, input: str | None = None, check: bool = True) -> object:
        print("+ " + shlex.join(args), flush=True)
        result = self.runner(list(args), input=input, text=True, capture_output=True)
        if check and getattr(result, "returncode", 0) != 0:
            raise Failure(f"command failed ({result.returncode}): {shlex.join(args)}\n{getattr(result, 'stderr', '')}")
        return result

    def kubectl(self, *args: str, input: str | None = None, check: bool = True) -> object:
        return self.run(["kubectl", "--kubeconfig", str(self.c.kubeconfig), *args], input=input, check=check)

    def flux(self, *args: str) -> object:
        return self.run(["flux", "--kubeconfig", str(self.c.kubeconfig), *args])

    # Only the platform: what the root applies (on flux-system, or on the test's source).
    # Branch environments from app smoke or hand runs sit in flux-system on their own
    # sources; they are not development's platform and are left alone.
    def kustomizations(self) -> list[dict]:
        items = json.loads(self.kubectl("-n", NS, "get", KS_LIST, "-o", "json").stdout)["items"]
        return [i for i in items if source_of(i) in ("flux-system", self.c.source)]

    def helmreleases(self) -> list[dict]:
        items = json.loads(self.kubectl("get", HR_LIST, "-A", "-o", "json").stdout)["items"]
        return [i for i in items if not applied_by_branch_environment(i)]

    def wait(self, what: str, problems: Callable[[], list[str]]) -> None:
        """Poll until `problems()` is empty, or fail with the last problems seen."""
        deadline = self.clock() + self.c.ready_timeout_s
        while True:
            found = problems()
            if not found:
                print(f"base-smoke: {what}: ready", flush=True)
                return
            if self.clock() >= deadline:
                raise Failure(f"{what}: not ready after {self.c.ready_timeout_s}s: " + "; ".join(found[:10]))
            self.sleep(self.c.poll_s)


def ready(item: dict) -> bool:
    return any(c.get("type") == "Ready" and c.get("status") == "True" for c in item.get("status", {}).get("conditions", []))


def message(item: dict) -> str:
    for c in item.get("status", {}).get("conditions", []):
        if c.get("type") == "Ready":
            return f"{item['metadata']['name']}: {c.get('message', '')[:160]}"
    return f"{item['metadata']['name']}: no Ready condition"


def not_ready(items: Iterable[dict]) -> list[str]:
    return [message(i) for i in items if not ready(i)]


def applied_by_branch_environment(item: dict) -> bool:
    labels = item.get("metadata", {}).get("labels") or {}
    return labels.get("kustomize.toolkit.fluxcd.io/name", "").startswith("branch-")


def source_of(item: dict) -> str:
    return item.get("spec", {}).get("sourceRef", {}).get("name", "")


def repoint(rendered: str, source: str) -> str:
    if SOURCE_REF not in rendered:
        raise Failure("rendered development Kustomizations have no flux-system sourceRef to repoint")
    return rendered.replace(SOURCE_REF, SOURCE_REF.replace("name: flux-system", f"name: {source}"))


def start(k: Cluster) -> None:
    c = k.c
    k.kubectl("-n", NS, "annotate", "kustomization", "flux-system", f"{STAMP}={c.slug}", f"{STAMP_TIME}={int(time.time())}", "--overwrite")
    k.flux("suspend", "kustomization", "flux-system", "-n", NS)
    root = json.loads(k.kubectl("-n", NS, "get", f"{GITREPO}/flux-system", "-o", "json").stdout)["spec"]
    source = {
        "apiVersion": "source.toolkit.fluxcd.io/v1",
        "kind": "GitRepository",
        "metadata": {"name": c.source, "namespace": NS, "labels": {STAMP: c.slug}},
        # A long interval: this test is of one commit, the branch is not expected to move.
        "spec": {"interval": "60m", "timeout": "60s", "url": root["url"], "secretRef": root["secretRef"],
                 "ref": {"branch": f"base-smoke/pr-{c.pr}"}},
    }
    k.kubectl("apply", "--server-side", "--field-manager=base-smoke", "--force-conflicts", "-f", "-", input=json.dumps(source))
    for child in ("infra", "apps"):
        rendered = k.run(["kubectl", "kustomize", str(c.head_dir / CLUSTER / child)]).stdout
        k.kubectl("apply", "--server-side", "--field-manager=base-smoke", "--force-conflicts", "-f", "-", input=repoint(rendered, c.source))


def settled(k: Cluster) -> None:
    c = k.c

    def problems() -> list[str]:
        found = []
        for item in k.kustomizations():
            if item["metadata"]["name"] == "flux-system":
                continue
            if source_of(item) != c.source:
                # Something restored development underneath the test; "all Ready" now means main.
                raise Failure(f"{item['metadata']['name']} is no longer on {c.source}; development was changed under the test")
            if c.sha not in item.get("status", {}).get("lastAppliedRevision", ""):
                found.append(f"{item['metadata']['name']}: has not applied {c.sha[:12]} yet")
            elif not ready(item):
                found.append(message(item))
        return found + not_ready(k.helmreleases())

    k.wait("development on the PR", problems)


def canaries(k: Cluster, stages: Stages) -> None:
    c = k.c
    tools = c.base_dir / "tools" / "development"
    for app in c.canaries:
        args = ["python3", str(tools / "verify_branch_deploy.py"), "--ci", "--app", app, "--branch", "main",
                "--slug", c.slug, "--kubeconfig", str(c.kubeconfig)]
        if app in BROWSER_CANARIES:
            args.append("--browser")
        try:
            with stages.stage(f"Canary {app} (from main)"):
                k.run(args)
        finally:
            k.run(["python3", str(tools / "cleanup_pr_envs.py"), "--kubeconfig", str(c.kubeconfig), "--slug", c.slug], check=False)


def restore(k: Cluster) -> None:
    c = k.c
    k.kubectl("-n", NS, "annotate", "kustomization", "flux-system", f"{STAMP}-", f"{STAMP_TIME}-", check=False)
    k.flux("resume", "kustomization", "flux-system", "-n", NS)
    k.flux("reconcile", "kustomization", "flux-system", "-n", NS, "--with-source")
    extras = [i["metadata"]["name"] for i in k.kustomizations() if source_of(i) == c.source]
    if extras:
        k.kubectl("-n", NS, "delete", KS, *extras, "--wait=true", "--timeout=600s")
    k.kubectl("-n", NS, "delete", f"{GITREPO}/{c.source}", "--ignore-not-found=true")
    k.wait("development restored to main", lambda: not_ready(k.kustomizations()) + not_ready(k.helmreleases()))


def run(config: Config, *, runner: Runner = subprocess.run, sleep=time.sleep, clock=time.monotonic) -> int:
    stages = Stages()
    outcome = 1
    try:
        outcome = run_stages(Cluster(config, runner, sleep, clock), stages)
    finally:
        try:
            append(config.step_summary, report(config, stages, outcome))
        except OSError as exc:
            print(f"base-smoke: could not write the job summary: {exc}", flush=True)
    return outcome


def run_stages(k: Cluster, stages: Stages) -> int:
    try:
        with stages.stage("Development healthy before the test"):
            k.wait("development before the test", lambda: not_ready(k.kustomizations()))
    except Failure as exc:
        print(f"base-smoke: FAILED: development is not healthy before the test, not touching it: {exc}", flush=True)
        return 1
    outcome = 0
    try:
        with stages.stage("Apply the PR to development"):
            start(k)
        with stages.stage("PR settled (every Kustomization on the merge commit, Ready)"):
            settled(k)
        canaries(k, stages)
        print("base-smoke: the PR's platform settled and the canaries passed", flush=True)
    except Failure as exc:
        print(f"base-smoke: FAILED: {exc}", flush=True)
        outcome = 1
    try:
        with stages.stage("Restore main"):
            restore(k)
    except Failure as exc:
        print(f"base-smoke: DEVELOPMENT DID NOT RECOVER: {exc}", flush=True)
        return 2
    return outcome


def report(c: Config, stages: Stages, outcome: int) -> str:
    verdict = {0: "passed", 1: "FAILED (development restored to main)"}.get(outcome, "DEVELOPMENT DID NOT RECOVER")
    planned = ("Development healthy before the test", "Apply the PR to development",
               "PR settled (every Kustomization on the merge commit, Ready)",
               *(f"Canary {app} (from main)" for app in c.canaries), "Restore main")
    return f"### Base smoke PR #{c.pr} at `{c.sha[:12]}`: {verdict}\n\n{stages.table(planned)}"


def recover_stale(kubeconfig: Path, *, max_age_s: int, runner: Runner = subprocess.run, now: float | None = None,
                  sleep=time.sleep, clock=time.monotonic) -> int:
    """Restore development if a base smoke test was killed mid-run: the root is suspended and
    stamped longer ago than `max_age_s`. A root suspended without the stamp was a person's
    choice and is left alone. Returns 0 when nothing was needed or the restore succeeded."""
    probe = Cluster(Config(kubeconfig, 0, "", Path("."), Path(".")), runner, sleep, clock)
    try:
        root = json.loads(probe.kubectl("-n", NS, "get", f"{KS}/flux-system", "-o", "json").stdout)
    except (Failure, ValueError) as exc:
        print(f"base-smoke: cannot read development's root Kustomization: {exc}", flush=True)
        return 2
    annotations = root.get("metadata", {}).get("annotations", {}) or {}
    slug, stamped = annotations.get(STAMP, ""), annotations.get(STAMP_TIME, "")
    if not root.get("spec", {}).get("suspend") or not slug.startswith("pr-") or not stamped.isdigit():
        print("base-smoke: no stale base smoke test to recover", flush=True)
        return 0
    age = (time.time() if now is None else now) - int(stamped)
    if age < max_age_s:
        print(f"base-smoke: {slug} has held development for {int(age)}s; leaving it running", flush=True)
        return 0
    print(f"base-smoke: {slug} left development suspended {int(age)}s ago; restoring", flush=True)
    k = Cluster(Config(kubeconfig, int(slug[3:]), "", Path("."), Path(".")), runner, sleep, clock)
    try:
        restore(k)
    except Failure as exc:
        print(f"base-smoke: DEVELOPMENT DID NOT RECOVER: {exc}", flush=True)
        return 2
    return 0


def install_signal_handlers() -> None:
    """Exit at once on cancellation. A cancelled job's always() step does the restore; a
    process that kept going would run on top of it."""
    def stop(signum, _frame):
        print(f"base-smoke: received signal {signum}; stopping (the job's always() step restores)", flush=True)
        raise SystemExit(128 + signum)

    signal.signal(signal.SIGTERM, stop)
    signal.signal(signal.SIGINT, stop)


def main(argv: Sequence[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--kubeconfig", type=Path, required=True)
    p.add_argument("--recover-stale", action="store_true",
                   help="only restore development if a killed test left the root suspended and stamped")
    p.add_argument("--max-age-seconds", type=int, default=3600,
                   help="with --recover-stale: how old the stamp must be (0 = restore now, for the job's own cleanup)")
    p.add_argument("--pr", type=int)
    p.add_argument("--sha", help="the merge commit of the PR onto main that base-smoke/pr-<N> points at")
    p.add_argument("--head-dir", type=Path, help="checkout of the PR head (rendered as data only)")
    p.add_argument("--base-dir", type=Path, default=Path("."), help="checkout of main (the tools that run)")
    a = p.parse_args(argv)
    install_signal_handlers()
    if a.recover_stale:
        return recover_stale(a.kubeconfig, max_age_s=a.max_age_seconds)
    if a.pr is None or not a.sha or a.head_dir is None:
        p.error("--pr, --sha and --head-dir are required unless --recover-stale")
    return run(Config(a.kubeconfig, a.pr, a.sha, a.head_dir, a.base_dir, step_summary=step_summary_path()))


if __name__ == "__main__":
    sys.exit(main())
