"""Renovate auto-merges only what dev-smoke deploys and tests in development.

An update auto-merges when every file it changes is one that development deploys:
a smoke-tested app's branch environment (the `smoke` job) or a file a development
Flux Kustomization renders (the `base` job). Major updates never auto-merge, and
Renovate merges itself only once every check on the PR is green, `dev-smoke`
included, rather than handing the PR to GitHub auto-merge, which waits for the
required checks only.
"""

from __future__ import annotations

import fnmatch
import json
import re
import subprocess
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
PROFILES = REPO_ROOT / "tools" / "development" / "smoke-profiles"
DEVELOPMENT = REPO_ROOT / "kubernetes" / "clusters" / "development"
ALLOWED_UPDATE_TYPES = {"minor", "patch", "digest", "pin", "pinDigest"}
# Kustomization fields whose entries name local files or directories.
REFERENCE_FIELDS = {
    "resources", "components", "patches", "patchesStrategicMerge", "patchesJson6902",
    "configMapGenerator", "secretGenerator", "configurations", "crds", "helmCharts",
    "transformers", "generators",
}
REFERENCE = re.compile(r"(?:^\s*-\s+|path:\s+|valuesFile:\s+|=)([^\s#=]+)\s*$")


def config() -> dict:
    return json.loads((REPO_ROOT / "renovate.json").read_text(encoding="utf-8"))


def automerge_rules() -> list[dict]:
    return [rule for rule in config().get("packageRules", []) if rule.get("automerge") is True]


def automerge_patterns() -> list[str]:
    return [pattern for rule in automerge_rules() for pattern in rule.get("matchFileNames", [])]


def references(directory: Path) -> list[Path]:
    """Local paths a kustomization.yaml names (remote URLs and missing paths are skipped)."""
    found: list[Path] = []
    field = None
    for line in (directory / "kustomization.yaml").read_text(encoding="utf-8").splitlines():
        top = re.match(r"^([A-Za-z0-9]+):", line)
        if top:
            field = top.group(1)
            continue
        if field not in REFERENCE_FIELDS:
            continue
        for candidate in REFERENCE.findall(line):
            path = (directory / candidate).resolve()
            if path.exists() and REPO_ROOT in path.parents:
                found.append(path)
    return found


def walk(start: Path, reached: set[Path]) -> None:
    start = start.resolve()
    if start.is_file():
        reached.add(start)
        return
    kustomization = start / "kustomization.yaml"
    if not kustomization.exists() or kustomization in reached:
        return
    reached.add(kustomization)
    for path in references(start):
        walk(path, reached)


def development_kustomization_paths() -> list[str]:
    paths = []
    for child in ("infra", "apps"):
        for file in sorted((DEVELOPMENT / child).glob("*.yaml")):
            for doc in re.split(r"(?m)^---\s*$", file.read_text(encoding="utf-8")):
                if re.search(r"(?m)^apiVersion: kustomize\.toolkit\.fluxcd\.io/", doc) and re.search(r"(?m)^kind: Kustomization$", doc):
                    paths.append(re.search(r"(?m)^  path: (?:\./)?(\S+)$", doc).group(1))
    return paths


def smoke_tested_apps() -> list[str]:
    apps = []
    for path in sorted(PROFILES.glob("*.json")):
        profile = json.loads(path.read_text(encoding="utf-8"))
        if profile.get("prSmoke") is True:
            apps.append(profile["app"])
    return apps


def deployed_by_development() -> set[str]:
    """Repo files that reach development: base Kustomizations plus smoke-tested branch overlays."""
    reached: set[Path] = set()
    for path in development_kustomization_paths():
        walk(REPO_ROOT / path, reached)
    for app in smoke_tested_apps():
        walk(REPO_ROOT / "kubernetes" / "apps" / app / "branch", reached)
    return {str(path.relative_to(REPO_ROOT)) for path in reached}


def tracked_files() -> list[str]:
    return subprocess.run(["git", "ls-files"], cwd=REPO_ROOT, capture_output=True, text=True, check=True).stdout.split()


def matched(pattern: str, files: list[str]) -> list[str]:
    return [f for f in files if fnmatch.fnmatchcase(f, pattern)]


class RenovateAutomergeTest(unittest.TestCase):
    def test_there_is_an_auto_merge_rule_and_nothing_auto_merges_outside_it(self) -> None:
        self.assertTrue(automerge_rules(), "no auto-merge rule")
        top = config()
        self.assertNotIn("automerge", top)
        for rule in automerge_rules():
            self.assertTrue(rule.get("matchFileNames"), f"an auto-merge rule must be limited to paths: {rule}")

    def test_renovate_merges_only_once_every_check_is_green(self) -> None:
        # GitHub auto-merge would wait for the required checks only, and dev-smoke is not one yet.
        self.assertIs(config().get("platformAutomerge"), False)
        for rule in automerge_rules():
            self.assertIs(rule.get("platformAutomerge", False), False)
            self.assertNotIn("ignoreTests", rule)

    def test_an_auto_merge_branch_is_not_rebased_just_for_being_behind_main(self) -> None:
        # Renovate runs once a day. Its default for auto-merge rules rebases a branch that is
        # behind main instead of merging it, so on an active main nothing would ever merge.
        # dev-smoke's smoke and base jobs already test the PR merged onto main as of their run.
        for rule in automerge_rules():
            self.assertEqual(rule.get("rebaseWhen"), "conflicted")

    def test_major_updates_never_auto_merge(self) -> None:
        for rule in automerge_rules():
            types = set(rule.get("matchUpdateTypes", []))
            self.assertTrue(types, f"an auto-merge rule must name its update types: {rule}")
            self.assertLessEqual(types, ALLOWED_UPDATE_TYPES)

    def test_patterns_are_whole_directories(self) -> None:
        # dev-smoke's guard (tools/development/classify_pr.py) matches them as directory prefixes.
        for pattern in automerge_patterns():
            self.assertRegex(pattern, r"^[\w./-]+/\*\*$")

    def test_every_auto_merge_file_is_deployed_by_development(self) -> None:
        deployed = deployed_by_development()
        files = [f for f in tracked_files() if not f.endswith(".md")]
        for pattern in automerge_patterns():
            hits = matched(pattern, files)
            self.assertTrue(hits, f"{pattern} matches nothing")
            missing = [f for f in hits if f not in deployed]
            self.assertEqual(missing, [], f"{pattern}: development does not deploy these, so dev-smoke would not test them")

    def test_production_only_and_unrehearsable_paths_never_auto_merge(self) -> None:
        for path in (
            "kubernetes/clusters/production/flux-system/gotk-components.yaml",
            "kubernetes/clusters/development/flux-system/gotk-components.yaml",
            "kubernetes/infra/authentik/app.yaml",
            "kubernetes/infra/monitoring/grafana/app.yaml",
            "kubernetes/apps/pihole/app.yaml",
            "kubernetes/apps/jellyfin/kustomization.yaml",
            "terraform/modules/talos-bootstrap/network.tf",
            ".github/workflows/dev-smoke.yml",
        ):
            for pattern in automerge_patterns():
                self.assertFalse(fnmatch.fnmatchcase(path, pattern), f"{path} matches {pattern}")

    def test_the_walk_sees_through_overlays(self) -> None:
        deployed = deployed_by_development()
        # cert-manager-development reaches the shared chart through ../cert-manager;
        # jellyfin's branch overlay reaches production's manifests through ../../base.
        self.assertIn("kubernetes/infra/controllers/cert-manager/app.yaml", deployed)
        self.assertIn("kubernetes/apps/jellyfin/base/app.yaml", deployed)
        self.assertNotIn("kubernetes/apps/pihole/app.yaml", deployed)


if __name__ == "__main__":
    unittest.main()
