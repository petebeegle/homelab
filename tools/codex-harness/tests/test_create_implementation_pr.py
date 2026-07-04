from __future__ import annotations

import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPT_SOURCE = REPO_ROOT / ".codex" / "scripts" / "create_implementation_pr.sh"
SDD_VALIDATOR = REPO_ROOT / "tools" / "codex-harness" / "validate_sdd_context.py"
VALIDATION_COMMON = REPO_ROOT / "tools" / "codex-harness" / "validation_common.py"
TOOLS_LIB_SOURCE = REPO_ROOT / "tools" / "lib"


class CreateImplementationPrTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmpdir = tempfile.TemporaryDirectory(prefix="pr-test-")
        self.root = Path(self.tmpdir.name)
        self.implementation = "pr-test"
        self.branch = f"codex/{self.implementation}"
        _init_repo(self.root)
        _install_harness_files(self.root)
        subprocess.run(["git", "switch", "-c", self.branch], cwd=self.root, check=True, stdout=subprocess.DEVNULL)
        self.head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=self.root, text=True).strip()
        _write_sdd_artifacts(self.root, self.implementation, final_head=self.head)

    def tearDown(self) -> None:
        self.tmpdir.cleanup()

    def test_blocks_without_evidence_md(self) -> None:
        (self.root / "specs" / self.implementation / "evidence.md").unlink()

        result = _run_script(self.root)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("evidence.md", result.stderr)

    def test_blocks_stale_evidence_head_without_verifier_files(self) -> None:
        _write_sdd_artifacts(self.root, self.implementation, final_head="0" * 40)

        result = _run_script(self.root)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("records HEAD", result.stderr)

    def test_blocks_dirty_tree_after_valid_sdd_evidence(self) -> None:
        (self.root / "README.md").write_text("# changed\n", encoding="utf-8")

        result = _run_script(self.root)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("working tree must be clean", result.stderr)

    def test_auto_exits_on_non_codex_branch(self) -> None:
        subprocess.run(["git", "switch", "main"], cwd=self.root, check=True, stdout=subprocess.DEVNULL)

        result = _run_script(self.root, "--auto")

        self.assertEqual(result.returncode, 0, result.stderr)


def _init_repo(root: Path) -> None:
    subprocess.run(["git", "init", "-b", "main"], cwd=root, check=True, stdout=subprocess.DEVNULL)
    subprocess.run(["git", "config", "user.email", "codex@example.invalid"], cwd=root, check=True)
    subprocess.run(["git", "config", "user.name", "Codex"], cwd=root, check=True)
    subprocess.run(["git", "remote", "add", "origin", "https://github.com/petebeegle/homelab.git"], cwd=root, check=True)
    (root / "README.md").write_text("# test\n", encoding="utf-8")
    subprocess.run(["git", "add", "README.md"], cwd=root, check=True)
    subprocess.run(["git", "commit", "-m", "test: initialize"], cwd=root, check=True, stdout=subprocess.DEVNULL)


def _install_harness_files(root: Path) -> None:
    script_path = root / ".codex" / "scripts" / "create_implementation_pr.sh"
    tool_dir = root / "tools" / "codex-harness"
    script_path.parent.mkdir(parents=True, exist_ok=True)
    tool_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(SCRIPT_SOURCE, script_path)
    shutil.copy2(SDD_VALIDATOR, tool_dir / "validate_sdd_context.py")
    shutil.copy2(VALIDATION_COMMON, tool_dir / "validation_common.py")
    shutil.copytree(TOOLS_LIB_SOURCE, root / "tools" / "lib")
    script_path.chmod(0o755)


def _write_sdd_artifacts(root: Path, implementation: str, *, final_head: str | None = None) -> None:
    specs = root / "specs" / implementation
    specs.mkdir(parents=True, exist_ok=True)
    (specs / "spec.md").write_text("# Spec\n", encoding="utf-8")
    (specs / "plan.md").write_text("# Plan\n", encoding="utf-8")
    (specs / "tasks.md").write_text("# Tasks\n", encoding="utf-8")
    lines = ["# Evidence"]
    if final_head is not None:
        lines.append(f"- Final HEAD: {final_head}")
    (specs / "evidence.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def _run_script(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["bash", ".codex/scripts/create_implementation_pr.sh", *args],
        cwd=root,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )


if __name__ == "__main__":
    unittest.main()
