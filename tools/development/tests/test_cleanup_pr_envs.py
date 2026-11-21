from __future__ import annotations

import contextlib
import io
import json
import sys
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from types import SimpleNamespace


REPO_ROOT = Path(__file__).resolve().parents[3]
TOOLS_DEVELOPMENT = REPO_ROOT / "tools" / "development"
if str(TOOLS_DEVELOPMENT) not in sys.path:
    sys.path.insert(0, str(TOOLS_DEVELOPMENT))

import cleanup_pr_envs as cleanup
from devverify.config import VerificationError

NOW = datetime(2026, 11, 15, 12, 0, 0, tzinfo=timezone.utc)
KS = "kustomization.kustomize.toolkit.fluxcd.io"
GR = "gitrepository.source.toolkit.fluxcd.io"


def item(kind: str, name: str, age: timedelta = timedelta(minutes=1)) -> dict:
    return {
        "kind": kind,
        "metadata": {"name": name, "creationTimestamp": (NOW - age).strftime("%Y-%m-%dT%H:%M:%SZ")},
    }


def kustomization(name: str, age: timedelta = timedelta(minutes=1)) -> dict:
    return item("Kustomization", name, age)


def gitrepository(name: str, age: timedelta = timedelta(minutes=1)) -> dict:
    return item("GitRepository", name, age)


class FakeKubectl:
    quiet = True

    def __init__(self, items: list[dict], *, fail_on: str | None = None, pvs: list[dict] | None = None) -> None:
        self.items = items
        self.pvs = pvs or []
        self.fail_on = fail_on
        self.calls: list[list[str]] = []

    def __call__(self, args: list[str], **kwargs: object) -> SimpleNamespace:
        self.calls.append(args)
        command = " ".join(args)
        if self.fail_on and self.fail_on in command:
            return SimpleNamespace(returncode=1, stdout="")
        if "get" in args and "persistentvolumes" in args:
            return SimpleNamespace(returncode=0, stdout=json.dumps({"items": self.pvs}))
        if "get" in args:
            return SimpleNamespace(returncode=0, stdout=json.dumps({"items": self.items}))
        return SimpleNamespace(returncode=0, stdout="")

    def patched_volumes(self) -> list[str]:
        return [c[c.index("persistentvolume") + 1] for c in self.calls if "patch" in c]

    def deletes(self) -> list[str]:
        return [" ".join(c) for c in self.calls if "delete" in c or "wait" in c]


ENVIRONMENT = [
    kustomization("branch-whoami-pr-12"),
    gitrepository("branch-pr-12"),
    kustomization("branch-whoami-pr-13"),
    gitrepository("branch-pr-13"),
    kustomization("branch-whoami-smoke", timedelta(days=30)),
    gitrepository("branch-smoke", timedelta(days=30)),
    gitrepository("branch-homepage-homepage-dashboard", timedelta(days=175)),
    kustomization("app-whoami", timedelta(days=180)),
    gitrepository("flux-system", timedelta(days=180)),
]


def pv(name: str, claim_namespace: str, *, phase: str = "Released", policy: str = "Retain",
       age: timedelta = timedelta(minutes=1)) -> dict:
    return {
        "metadata": {"name": name, "creationTimestamp": (NOW - age).strftime("%Y-%m-%dT%H:%M:%SZ")},
        "spec": {"persistentVolumeReclaimPolicy": policy, "claimRef": {"namespace": claim_namespace, "name": "data"}},
        "status": {"phase": phase},
    }


class BranchVolumeCleanupTest(unittest.TestCase):
    """Development's StorageClasses Retain; a branch environment's volumes would outlive it on the NAS."""

    def run_cleanup(self, pvs: list[dict], **kwargs) -> tuple[list[str], FakeKubectl]:
        fake = FakeKubectl(ENVIRONMENT, pvs=pvs)
        deleted = cleanup.cleanup_pr_envs(kubeconfig=Path("/tmp/kc"), runner=fake, now=NOW, **kwargs)
        return deleted, fake

    def test_slug_releases_only_that_slugs_released_retained_volumes(self) -> None:
        pvs = [
            pv("pvc-a", "whoami-pr-12"),
            pv("pvc-b", "whoami-pr-13"),
            pv("pvc-c", "whoami-pr-12", phase="Bound"),
            pv("pvc-d", "whoami-pr-12", policy="Delete"),
            pv("pvc-e", "whoami"),
        ]
        deleted, fake = self.run_cleanup(pvs, slug="pr-12")
        self.assertEqual(fake.patched_volumes(), ["pvc-a"])
        self.assertIn("persistentvolume/pvc-a", deleted)
        patch = next(c for c in fake.calls if "patch" in c)
        self.assertIn('{"spec":{"persistentVolumeReclaimPolicy":"Delete"}}', patch)

    def test_older_than_also_finds_volumes_whose_environment_is_already_gone(self) -> None:
        pvs = [
            pv("old", "immich-pr-9", age=timedelta(hours=5)),
            pv("young", "immich-pr-9", age=timedelta(minutes=10)),
        ]
        _, fake = self.run_cleanup(pvs, older_than_seconds=3 * 3600)
        self.assertEqual(fake.patched_volumes(), ["old"])

    def test_volumes_outside_pr_environments_are_never_touched(self) -> None:
        pvs = [
            pv("hand-run", "home-assistant-home-assistant-ui-automation", age=timedelta(days=90)),
            pv("prod-name", "immich", age=timedelta(days=90)),
            pv("cnpg", "immich-pr-9-extra", age=timedelta(days=90)),
        ]
        _, fake = self.run_cleanup(pvs, older_than_seconds=3600)
        self.assertEqual(fake.patched_volumes(), [])


class CleanupPrEnvsTest(unittest.TestCase):
    def run_cleanup(self, items: list[dict], **kwargs) -> tuple[list[str], FakeKubectl]:
        fake = FakeKubectl(items, fail_on=kwargs.pop("fail_on", None))
        deleted = cleanup.cleanup_pr_envs(kubeconfig=Path("/tmp/kc"), runner=fake, now=NOW, **kwargs)
        return deleted, fake

    def test_slug_deletes_only_that_slugs_objects_and_waits_for_the_namespace(self) -> None:
        deleted, fake = self.run_cleanup(ENVIRONMENT, slug="pr-12")
        self.assertEqual(sorted(deleted), ["gitrepository/branch-pr-12", "kustomization/branch-whoami-pr-12"])
        joined = "\n".join(fake.deletes())
        self.assertIn(f"delete {KS}/branch-whoami-pr-12", joined)
        self.assertIn("wait namespace/whoami-pr-12 --for=delete", joined)
        self.assertIn(f"delete {GR}/branch-pr-12", joined)
        self.assertNotIn("pr-13", joined)

    def test_older_than_deletes_only_environments_past_the_threshold(self) -> None:
        items = [
            kustomization("branch-whoami-pr-12", timedelta(hours=5)),
            gitrepository("branch-pr-12", timedelta(hours=5)),
            kustomization("branch-whoami-pr-13", timedelta(minutes=10)),
            gitrepository("branch-pr-13", timedelta(minutes=10)),
        ]
        deleted, _ = self.run_cleanup(items, older_than_seconds=3 * 3600)
        self.assertEqual(sorted(deleted), ["gitrepository/branch-pr-12", "kustomization/branch-whoami-pr-12"])

    def test_listing_names_both_resource_types_in_one_comma_separated_argument(self) -> None:
        # `kubectl get A B` reads B as an object name of type A, so the two types must be one
        # comma-separated argument. The fake kubectl above accepts anything, so pin the shape here.
        _, fake = self.run_cleanup(ENVIRONMENT, slug="pr-12")
        get = next(call for call in fake.calls if "get" in call)
        index = get.index("get")
        self.assertEqual(f"{cleanup.KUSTOMIZATION},{cleanup.GITREPOSITORY}", get[index + 1])
        self.assertTrue(get[index + 2].startswith("-"), f"unexpected extra positional: {get[index + 2]}")

    def test_non_pr_objects_are_never_touched_even_when_very_old(self) -> None:
        deleted, fake = self.run_cleanup(ENVIRONMENT, older_than_seconds=60)
        self.assertEqual(sorted(deleted), sorted(
            ["gitrepository/branch-pr-12", "kustomization/branch-whoami-pr-12",
             "gitrepository/branch-pr-13", "kustomization/branch-whoami-pr-13"]))
        joined = "\n".join(fake.deletes())
        for protected in ("smoke", "homepage-dashboard", "app-whoami", f"{GR}/flux-system"):
            self.assertNotIn(protected, joined)

    def test_hyphenated_app_names_are_parsed(self) -> None:
        deleted, fake = self.run_cleanup(
            [kustomization("branch-home-assistant-pr-5"), gitrepository("branch-pr-5")], slug="pr-5"
        )
        self.assertIn("kustomization/branch-home-assistant-pr-5", deleted)
        self.assertIn("wait namespace/home-assistant-pr-5 --for=delete", "\n".join(fake.deletes()))

    def test_nothing_to_delete_returns_empty_and_runs_no_delete(self) -> None:
        deleted, fake = self.run_cleanup([gitrepository("flux-system")], slug="pr-12")
        self.assertEqual(deleted, [])
        self.assertEqual(fake.deletes(), [])

    def test_exactly_one_selector_and_a_safe_slug_are_required(self) -> None:
        fake = FakeKubectl([])
        for kwargs in (
            {},
            {"slug": "pr-12", "older_than_seconds": 60},
            {"slug": "smoke"},
            {"slug": "pr-12; rm -rf /"},
            {"slug": "pr-"},
        ):
            with self.assertRaises(ValueError, msg=str(kwargs)):
                cleanup.cleanup_pr_envs(kubeconfig=Path("/tmp/kc"), runner=fake, now=NOW, **kwargs)
        self.assertEqual(fake.calls, [])

    def test_a_failed_delete_is_reported_not_swallowed(self) -> None:
        with self.assertRaises(VerificationError):
            self.run_cleanup(ENVIRONMENT, slug="pr-12", fail_on=f"delete {KS}")

    def test_cli_prints_what_it_deleted(self) -> None:
        fake = FakeKubectl(ENVIRONMENT)
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = cleanup.main(["--kubeconfig", "/tmp/kc", "--slug", "pr-12"], runner=fake)
        self.assertEqual(code, 0)
        self.assertIn("kustomization/branch-whoami-pr-12", out.getvalue())

    def test_cli_older_than_accepts_durations(self) -> None:
        fake = FakeKubectl([])
        self.assertEqual(cleanup.main(["--kubeconfig", "/tmp/kc", "--older-than", "3h"], runner=fake), 0)


if __name__ == "__main__":
    unittest.main()
