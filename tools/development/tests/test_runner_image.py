from __future__ import annotations

import json
import re
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
DOCKERFILE = REPO_ROOT / "tools" / "ci" / "runner-image" / "Dockerfile"
WORKFLOW = REPO_ROOT / ".github" / "workflows" / "runner-image.yml"
PACKAGE_JSON = REPO_ROOT / "tests" / "browser" / "package.json"


class RunnerImageTest(unittest.TestCase):
    def read(self, path: Path) -> str:
        self.assertTrue(path.exists(), f"missing: {path.relative_to(REPO_ROOT)}")
        return path.read_text(encoding="utf-8")

    def test_playwright_versions_match(self) -> None:
        base = re.search(r"^FROM mcr\.microsoft\.com/playwright:v(\d+\.\d+\.\d+)-noble\s*$", self.read(DOCKERFILE), re.M)
        self.assertIsNotNone(base, "FROM must be a pinned mcr.microsoft.com/playwright:v<version>-noble tag")
        package = json.loads(PACKAGE_JSON.read_text(encoding="utf-8"))["devDependencies"]["@playwright/test"]
        self.assertEqual(base.group(1), package)

    def test_every_download_is_checksum_verified(self) -> None:
        text = self.read(DOCKERFILE)
        for tool in ("RUNNER", "KUBECTL", "FLUX"):
            self.assertRegex(text, rf"ARG {tool}_SHA256=[0-9a-f]{{64}}\b", tool)
        self.assertGreaterEqual(text.count("sha256sum -c"), 3)

    def test_runs_as_a_non_root_user(self) -> None:
        users = re.findall(r"^USER (\S+)\s*$", self.read(DOCKERFILE), re.M)
        self.assertTrue(users)
        self.assertNotIn(users[-1], ("root", "0"))

    def test_runner_lives_where_arc_expects_it(self) -> None:
        text = self.read(DOCKERFILE)
        self.assertIn("/home/runner", text)
        self.assertRegex(text, r"actions-runner-linux-x64-\$\{RUNNER_VERSION\}")

    def test_workflow_builds_on_prs_and_pushes_only_off_prs(self) -> None:
        text = self.read(WORKFLOW)
        self.assertIn("pull_request:", text)
        self.assertIn("tools/ci/runner-image/**", text)
        self.assertIn("packages: write", text)
        steps = re.split(r"\n      - name: ", text)
        pushing = [step for step in steps if "docker push" in step]
        self.assertTrue(pushing)
        for step in pushing:
            self.assertIn("if: github.event_name != 'pull_request'", step)
        login = [step for step in steps if "docker/login-action" in step]
        self.assertTrue(login)
        for step in login:
            self.assertIn("if: github.event_name != 'pull_request'", step)

    def test_workflow_smokes_the_built_image_before_pushing(self) -> None:
        text = self.read(WORKFLOW)
        for tool in ("kubectl version --client", "flux --version", "python3 --version", "node --version"):
            self.assertIn(tool, text)
        self.assertLess(text.index("kubectl version --client"), text.index("docker push"))


if __name__ == "__main__":
    unittest.main()
