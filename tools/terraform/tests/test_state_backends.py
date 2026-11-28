from __future__ import annotations

import re
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
TERRAFORM = REPO_ROOT / "terraform"


def roots() -> list[Path]:
    """Every directory Terraform is run in: has .tf files and is not a module."""
    found = {path.parent for path in TERRAFORM.rglob("*.tf") if ".terraform" not in path.parts}
    return sorted(path for path in found if "modules" not in path.relative_to(TERRAFORM).parts)


def backend(root: Path) -> str:
    text = "\n".join(path.read_text(encoding="utf-8") for path in sorted(root.glob("*.tf")))
    match = re.search(r'(?ms)^  backend "s3" \{\n(.*?)^  \}', text)
    assert match, f'{root.relative_to(REPO_ROOT)} has no backend "s3" block'
    return match.group(1)


def setting(block: str, name: str) -> str | None:
    match = re.search(rf"(?m)^\s+{name}\s+=\s+(.+?)\s*$", block)
    return match.group(1) if match else None


class StateBackendTest(unittest.TestCase):
    def test_the_roots_are_the_ones_this_test_knows(self) -> None:
        # A new root must get a backend, and this list, in the same change.
        self.assertEqual(
            [str(root.relative_to(TERRAFORM)) for root in roots()],
            ["development", "external/grafana", "external/nexus", "external/synology", "production"],
        )

    def test_every_root_keeps_state_in_the_nas_bucket_with_a_lock(self) -> None:
        for root in roots():
            with self.subTest(root=str(root.relative_to(REPO_ROOT))):
                block = backend(root)
                self.assertEqual(setting(block, "bucket"), '"terraform-state"')
                self.assertEqual(setting(block, "endpoints"), '{ s3 = "https://s3.petebeegle.com" }')
                self.assertEqual(setting(block, "use_path_style"), "true")
                self.assertEqual(setting(block, "use_lockfile"), "true")

    def test_each_root_has_its_own_key_named_after_its_path(self) -> None:
        for root in roots():
            with self.subTest(root=str(root.relative_to(REPO_ROOT))):
                expected = f'"{root.relative_to(TERRAFORM).as_posix()}/terraform.tfstate"'
                self.assertEqual(setting(backend(root), "key"), expected)

    def test_no_root_carries_credentials(self) -> None:
        # Keys come from AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY (1Password), never from code.
        for root in roots():
            with self.subTest(root=str(root.relative_to(REPO_ROOT))):
                block = backend(root)
                for name in ("access_key", "secret_key", "token", "profile", "shared_credentials_files"):
                    self.assertIsNone(setting(block, name), name)


if __name__ == "__main__":
    unittest.main()
