from __future__ import annotations

import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
HOOK_SOURCE = REPO_ROOT / ".codex" / "hooks" / "verifier_push_guard.sh"
SDD_VALIDATOR = REPO_ROOT / "tools" / "codex-harness" / "validate_sdd_context.py"
VALIDATION_COMMON = REPO_ROOT / "tools" / "codex-harness" / "validation_common.py"
TOOLS_LIB_SOURCE = REPO_ROOT / "tools" / "lib"


class SpecKitPushGuardTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmpdir = tempfile.TemporaryDirectory(prefix="push-test-")
        self.root = Path(self.tmpdir.name)
        self.implementation = "push-test"
        self.branch = f"codex/{self.implementation}"
        _init_repo(self.root)
        _install_harness_files(self.root)
        subprocess.run(["git", "switch", "-c", self.branch], cwd=self.root, check=True, stdout=subprocess.DEVNULL)
        _write_sdd_artifacts(self.root, self.implementation)

    def tearDown(self) -> None:
        self.tmpdir.cleanup()

    def test_allows_valid_spec_kit_branch_without_verifier_files(self) -> None:
        result = _run_hook(self.root)

        self.assertEqual(result.returncode, 0, result.stderr)

    def test_blocks_main_branch(self) -> None:
        subprocess.run(["git", "switch", "main"], cwd=self.root, check=True, stdout=subprocess.DEVNULL)

        result = _run_hook(self.root)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Current branch is main", result.stderr)

    def test_blocks_non_codex_branch(self) -> None:
        subprocess.run(["git", "switch", "-c", "feature/test"], cwd=self.root, check=True, stdout=subprocess.DEVNULL)

        result = _run_hook(self.root)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("does not match codex/<implementation>", result.stderr)

    def test_blocks_without_evidence(self) -> None:
        (self.root / "specs" / self.implementation / "evidence.md").unlink()

        result = _run_hook(self.root)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("evidence.md", result.stderr)


def _init_repo(root: Path) -> None:
    subprocess.run(["git", "init", "-b", "main"], cwd=root, check=True, stdout=subprocess.DEVNULL)
    subprocess.run(["git", "config", "user.email", "codex@example.invalid"], cwd=root, check=True)
    subprocess.run(["git", "config", "user.name", "Codex"], cwd=root, check=True)
    subprocess.run(["git", "remote", "add", "origin", "https://github.com/petebeegle/homelab.git"], cwd=root, check=True)
    (root / "README.md").write_text("# test\n", encoding="utf-8")
    subprocess.run(["git", "add", "README.md"], cwd=root, check=True)
    subprocess.run(["git", "commit", "-m", "test: initialize"], cwd=root, check=True, stdout=subprocess.DEVNULL)


def _install_harness_files(root: Path) -> None:
    hook_path = root / ".codex" / "hooks" / "verifier_push_guard.sh"
    tool_dir = root / "tools" / "codex-harness"
    hook_path.parent.mkdir(parents=True, exist_ok=True)
    tool_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(HOOK_SOURCE, hook_path)
    shutil.copy2(SDD_VALIDATOR, tool_dir / "validate_sdd_context.py")
    shutil.copy2(VALIDATION_COMMON, tool_dir / "validation_common.py")
    shutil.copytree(TOOLS_LIB_SOURCE, root / "tools" / "lib")
    hook_path.chmod(0o755)


def _write_sdd_artifacts(root: Path, implementation: str) -> None:
    specs = root / "specs" / implementation
    specs.mkdir(parents=True, exist_ok=True)
    (specs / "spec.md").write_text("# Spec\n", encoding="utf-8")
    (specs / "plan.md").write_text("# Plan\n", encoding="utf-8")
    (specs / "tasks.md").write_text("# Tasks\n", encoding="utf-8")
    (specs / "evidence.md").write_text("# Evidence\n", encoding="utf-8")


def _run_hook(root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["bash", ".codex/hooks/verifier_push_guard.sh", "origin", "https://github.com/petebeegle/homelab.git"],
        cwd=root,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )


if __name__ == "__main__":
    unittest.main()
