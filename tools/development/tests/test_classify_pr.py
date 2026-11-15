from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
TOOLS_DEVELOPMENT = REPO_ROOT / "tools" / "development"
if str(TOOLS_DEVELOPMENT) not in sys.path:
    sys.path.insert(0, str(TOOLS_DEVELOPMENT))

import classify_pr
from devverify.profiles import load_smoke_profile_file, load_smoke_profiles


class ClassifyPrTest(unittest.TestCase):
    def setUp(self) -> None:
        self.profiles = load_smoke_profiles()

    def classify(self, *files: str) -> classify_pr.Classification:
        return classify_pr.classify(list(files), self.profiles)

    def test_whoami_file_is_tested_with_browser(self) -> None:
        result = self.classify("kubernetes/apps/whoami/whoami.yaml")
        self.assertEqual((result.tested, result.app, result.browser), (True, "whoami", True))

    def test_homepage_file_is_tested_without_browser(self) -> None:
        result = self.classify("kubernetes/apps/homepage/base/deployment.yaml")
        self.assertEqual((result.tested, result.app, result.browser), (True, "homepage", False))

    def test_several_files_in_one_app_are_tested(self) -> None:
        result = self.classify("kubernetes/apps/whoami/whoami.yaml", "kubernetes/apps/whoami/branch/whoami.yaml")
        self.assertEqual((result.tested, result.app), (True, "whoami"))

    def test_two_apps_are_not_tested(self) -> None:
        result = self.classify("kubernetes/apps/whoami/whoami.yaml", "kubernetes/apps/homepage/base/deployment.yaml")
        self.assertFalse(result.tested)
        self.assertIn("multiple apps", result.reason)

    def test_app_plus_unrelated_file_is_not_tested(self) -> None:
        result = self.classify("kubernetes/apps/whoami/whoami.yaml", "README.md")
        self.assertFalse(result.tested)
        self.assertIn("README.md", result.reason)

    def test_terraform_change_is_not_tested(self) -> None:
        result = self.classify("terraform/development/variables.tf")
        self.assertFalse(result.tested)
        self.assertIn("terraform", result.reason)

    def test_terraform_wins_over_a_profiled_app(self) -> None:
        result = self.classify("kubernetes/apps/whoami/whoami.yaml", "terraform/development/variables.tf")
        self.assertFalse(result.tested)
        self.assertIn("terraform", result.reason)

    def test_verifier_and_browser_test_changes_are_not_tested(self) -> None:
        for path in ("tools/development/devverify/cli.py", "tests/browser/tests/whoami.spec.cjs"):
            result = self.classify(path)
            self.assertFalse(result.tested, path)
            self.assertIn("verifier", result.reason, path)

    def test_app_without_pr_smoke_is_not_tested(self) -> None:
        result = self.classify("kubernetes/apps/jellyfin/base/deployment.yaml")
        self.assertFalse(result.tested)
        self.assertIn("jellyfin", result.reason)

    def test_unknown_app_directory_is_not_tested(self) -> None:
        self.assertFalse(self.classify("kubernetes/apps/nope/x.yaml").tested)

    def test_file_directly_under_apps_is_not_in_any_app(self) -> None:
        result = self.classify("kubernetes/apps/kustomization.yaml")
        self.assertFalse(result.tested)
        self.assertIn("outside a profiled app", result.reason)

    def test_empty_change_list_is_not_tested(self) -> None:
        result = self.classify()
        self.assertFalse(result.tested)
        self.assertEqual(result.reason, "no changes")

    def test_only_whoami_and_homepage_opt_in(self) -> None:
        self.assertEqual({app for app, p in self.profiles.items() if p.pr_smoke}, {"whoami", "homepage"})

    def test_pr_smoke_must_be_a_boolean(self) -> None:
        profile = json.loads((TOOLS_DEVELOPMENT / "smoke-profiles" / "whoami.json").read_text(encoding="utf-8"))
        profile["prSmoke"] = "yes"
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "whoami.json"
            path.write_text(json.dumps(profile), encoding="utf-8")
            with self.assertRaises(Exception):
                load_smoke_profile_file(path)

    def test_cli_reads_stdin_and_prints_json(self) -> None:
        out = subprocess.run(
            [sys.executable, "-B", str(TOOLS_DEVELOPMENT / "classify_pr.py")],
            input="kubernetes/apps/whoami/whoami.yaml\n",
            capture_output=True,
            text=True,
            check=True,
        ).stdout
        self.assertEqual(json.loads(out), {"tested": True, "app": "whoami", "browser": True, "reason": "ok"})


if __name__ == "__main__":
    unittest.main()
