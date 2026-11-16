from __future__ import annotations

import json
import re
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
APPS = REPO_ROOT / "kubernetes" / "apps"
PROFILES = REPO_ROOT / "tools" / "development" / "smoke-profiles"
IMAGE = re.compile(r"^\s*(?:-\s+)?image:\s*['\"]?([^\s'\"#]+)", re.M)


def images(paths: list[Path]) -> set[str]:
    found: set[str] = set()
    for path in paths:
        found.update(IMAGE.findall(path.read_text(encoding="utf-8")))
    return found


def smoke_tested_apps() -> list[str]:
    return sorted(
        json.loads(path.read_text(encoding="utf-8"))["app"]
        for path in PROFILES.glob("*.json")
        if json.loads(path.read_text(encoding="utf-8")).get("prSmoke") is True
    )


class BranchOverlayImagesTest(unittest.TestCase):
    """The PR smoke test deploys kubernetes/apps/<app>/branch/, a copy of the app's manifests.

    If an image changes in only one copy, the smoke test passes without having tested the
    change. Keep the images in step so a green dev-smoke means the new image was deployed.
    """

    def test_there_are_smoke_tested_apps_to_check(self) -> None:
        self.assertTrue(smoke_tested_apps())

    def test_branch_copy_uses_the_same_images_as_the_real_manifests(self) -> None:
        for app in smoke_tested_apps():
            app_dir = APPS / app
            branch_files = sorted((app_dir / "branch").rglob("*.yaml"))
            real_files = sorted(p for p in app_dir.rglob("*.yaml") if (app_dir / "branch") not in p.parents)
            self.assertTrue(branch_files, f"{app} has no branch overlay")
            self.assertTrue(real_files, f"{app} has no manifests")
            real, branch = images(real_files), images(branch_files)
            self.assertTrue(real, f"{app}: found no images in the real manifests")
            self.assertEqual(
                real,
                branch,
                f"{app}: images differ between kubernetes/apps/{app}/ and kubernetes/apps/{app}/branch/ "
                "(update both, or the PR smoke test does not exercise the change)",
            )


if __name__ == "__main__":
    unittest.main()
