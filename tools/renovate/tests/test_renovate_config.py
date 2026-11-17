"""Keep Renovate PRs passing CI by construction.

Each test pins a cause of a recurring red Renovate PR (docs/runbooks/renovate.md).
"""
from __future__ import annotations

import fnmatch
import json
import re
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
CONFIG = REPO_ROOT / "renovate.json"
PLAYWRIGHT_PACKAGES = ("@playwright/test", "mcr.microsoft.com/playwright")
PLAYWRIGHT_FILES = (
    "tests/browser/package.json",
    "tests/smoke/package.json",
    "tests/smoke/package-lock.json",
    "kubernetes/apps/synthetics/smoke/package.json",
    "kubernetes/apps/synthetics/smoke/package-lock.json",
    "kubernetes/apps/synthetics/cronjob.yaml",
    "tools/ci/runner-image/Dockerfile",
)

PROVIDER_BLOCK = re.compile(r"(?m)^\s*(\w[\w-]*)\s*=\s*\{\s*\n\s*source\s*=\s*\"([^\"]+)\"\s*\n\s*version\s*=\s*\"([^\"]+)\"")
REQUIRED_PROVIDERS = re.compile(r"required_providers\s*\{(?P<body>.*?)\n  \}", re.S)
LOCAL_MODULE = re.compile(r"(?m)^\s*source\s*=\s*\"(\.{1,2}/[^\"]+)\"")
LOCKED = re.compile(r'provider "registry\.terraform\.io/([^"]+)" \{\s*\n\s*version\s*=\s*"([^"]+)"')


def config() -> dict:
    return json.loads(CONFIG.read_text(encoding="utf-8"))


def required_providers(directory: Path) -> dict[str, str]:
    providers: dict[str, str] = {}
    for path in sorted(directory.glob("*.tf")):
        for block in REQUIRED_PROVIDERS.finditer(path.read_text(encoding="utf-8")):
            for _, source, version in PROVIDER_BLOCK.findall(block.group("body")):
                providers[source] = version
    return providers


def local_modules(directory: Path, seen: set[Path] | None = None) -> set[Path]:
    seen = set() if seen is None else seen
    for path in sorted(directory.glob("*.tf")):
        for source in LOCAL_MODULE.findall(path.read_text(encoding="utf-8")):
            module = (directory / source).resolve()
            if module not in seen:
                seen.add(module)
                local_modules(module, seen)
    return seen


def terraform_roots() -> list[Path]:
    return sorted(path.parent for path in (REPO_ROOT / "terraform").rglob(".terraform.lock.hcl") if ".terraform" not in path.parent.parts)


class PlaywrightTest(unittest.TestCase):
    def test_image_and_npm_package_update_in_one_group(self) -> None:
        groups = {
            rule.get("groupName")
            for rule in config().get("packageRules", [])
            for name in PLAYWRIGHT_PACKAGES
            if name in rule.get("matchPackageNames", []) and rule.get("groupName")
        }
        self.assertEqual(len(groups), 1, f"one packageRule groupName must cover {PLAYWRIGHT_PACKAGES}, found {groups}")

    def test_no_playwright_pin_is_hidden_by_ignore_paths(self) -> None:
        # config:recommended ignores **/tests/**, which hid tests/browser and tests/smoke
        # from Renovate; ignorePaths is not merged, so the repo value replaces the preset.
        ignored = config().get("ignorePaths")
        self.assertIsNotNone(ignored, "set ignorePaths; the config:recommended default ignores **/tests/**")
        for path in PLAYWRIGHT_FILES:
            self.assertTrue((REPO_ROOT / path).is_file(), path)
            for pattern in ignored:
                self.assertFalse(fnmatch.fnmatch(path, pattern), f"{path} is ignored by {pattern}")

    def test_synthetics_image_matches_its_npm_package(self) -> None:
        # The synthetics CronJob skips the browser download, so the image must carry
        # the browsers for the exact @playwright/test version it installs.
        image = re.search(
            r"image: mcr\.microsoft\.com/playwright:v(\S+?)-noble",
            (REPO_ROOT / "kubernetes/apps/synthetics/cronjob.yaml").read_text(encoding="utf-8"),
        )
        self.assertIsNotNone(image)
        for package in ("kubernetes/apps/synthetics/smoke/package.json", "tests/smoke/package.json"):
            pinned = json.loads((REPO_ROOT / package).read_text(encoding="utf-8"))["devDependencies"]["@playwright/test"]
            self.assertEqual(image.group(1), pinned, package)


class TerraformLockFileTest(unittest.TestCase):
    """Renovate updates a .terraform.lock.hcl only for a provider declared in a .tf file
    in the lock file's directory (or below it). A provider declared only in a shared
    module under terraform/modules/ gets its constraint bumped but not the root lock
    files, and `terraform init` then fails. So each root redeclares its modules' providers."""

    def test_roots_are_found(self) -> None:
        roots = {path.relative_to(REPO_ROOT).as_posix() for path in terraform_roots()}
        self.assertIn("terraform/production", roots)
        self.assertIn("terraform/development", roots)

    def test_each_root_declares_every_module_provider_at_the_same_version(self) -> None:
        for root in terraform_roots():
            declared = required_providers(root)
            for module in local_modules(root):
                if module.is_relative_to(root):
                    continue  # Renovate finds the lock file from a module below the root
                for source, version in required_providers(module).items():
                    with self.subTest(root=root.relative_to(REPO_ROOT).as_posix(), module=module.relative_to(REPO_ROOT).as_posix(), provider=source):
                        self.assertEqual(declared.get(source), version)

    def test_lock_files_match_the_exact_constraints(self) -> None:
        for root in terraform_roots():
            locked = dict(LOCKED.findall((root / ".terraform.lock.hcl").read_text(encoding="utf-8")))
            for source, version in required_providers(root).items():
                with self.subTest(root=root.relative_to(REPO_ROOT).as_posix(), provider=source):
                    self.assertEqual(locked.get(source), version)


if __name__ == "__main__":
    unittest.main()
