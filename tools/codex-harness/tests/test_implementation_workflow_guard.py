from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
HOOK_SOURCE = REPO_ROOT / ".codex" / "hooks" / "implementation_workflow_guard.sh"
ACTIVE_VALIDATOR = REPO_ROOT / "tools" / "codex-harness" / "validate_active_implementation.py"
PLAN_VALIDATOR = REPO_ROOT / "tools" / "codex-harness" / "validate_implementation_plan.py"
ATTESTATION_VALIDATOR = REPO_ROOT / "tools" / "codex-harness" / "validate_workflow_attestations.py"


class ImplementationWorkflowGuardTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_parent = tempfile.TemporaryDirectory(prefix="guard-root-")
        self.sibling_root = Path(self.temp_parent.name) / "homelab-ideas"
        self.sibling_root.mkdir()
        self.tmpdir = tempfile.TemporaryDirectory(dir=self.sibling_root, prefix="guard-test-")
        self.root = Path(self.tmpdir.name)
        self.implementation = self.root.name
        self.branch = f"codex/{self.implementation}"
        self._init_repo()
        self._install_harness_files()

    def tearDown(self) -> None:
        self.tmpdir.cleanup()
        self.temp_parent.cleanup()

    def test_post_change_blocks_without_plan(self) -> None:
        self._switch_to_implementation_branch()
        self._write_marker()
        (self.root / "README.md").write_text("# changed\n", encoding="utf-8")

        result = self._run_hook()

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Missing .codex/tmp/implementation-plan.yaml", result.stderr)

    def test_post_change_blocks_without_owner_attestation(self) -> None:
        self._switch_to_implementation_branch()
        self._write_marker()
        self._write_plan()
        (self.root / "README.md").write_text("# changed\n", encoding="utf-8")

        result = self._run_hook()

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Missing .codex/tmp/implementation-owner-attestation.yaml", result.stderr)

    def test_post_change_allows_matching_marker_plan_and_owner_attestation(self) -> None:
        self._switch_to_implementation_branch()
        self._write_marker()
        self._write_plan()
        self._write_owner_attestation()
        (self.root / "README.md").write_text("# changed\n", encoding="utf-8")

        result = self._run_hook()

        self.assertEqual(result.returncode, 0, result.stderr)

    def test_preflight_bash_blocks_mutating_command_without_plan(self) -> None:
        self._switch_to_implementation_branch()
        self._write_marker()

        result = self._run_hook("--preflight-bash", {"command": "git add README.md"})

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Missing .codex/tmp/implementation-plan.yaml", result.stderr)

    def test_preflight_bash_allows_read_only_command_without_plan(self) -> None:
        result = self._run_hook("--preflight-bash", {"command": "git status --short"})

        self.assertEqual(result.returncode, 0, result.stderr)

    def test_preflight_bash_allows_workflow_bootstrap_commands_without_plan(self) -> None:
        clone = self._run_hook(
            "--preflight-bash",
            {
                "command": (
                    "git clone https://github.com/petebeegle/homelab.git "
                    f"{self.sibling_root}/bootstrap-test"
                )
            },
        )
        branch = self._run_hook(
            "--preflight-bash",
            {"command": "git switch -c codex/bootstrap-test origin/main"},
        )

        self.assertEqual(clone.returncode, 0, clone.stderr)
        self.assertEqual(branch.returncode, 0, branch.stderr)

    def test_preflight_bash_blocks_branch_bootstrap_outside_sibling_clone(self) -> None:
        with tempfile.TemporaryDirectory(prefix="planner-test-") as directory:
            root = Path(directory)
            self._init_external_repo(root)
            self._install_harness_files(root)

            result = self._run_hook(
                "--preflight-bash",
                {"command": "git switch -c codex/bootstrap-test origin/main"},
                cwd=root,
            )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Current branch is main", result.stderr)

    def test_preflight_mutation_allows_workflow_bootstrap_paths(self) -> None:
        result = self._run_hook(
            "--preflight-mutation",
            {"tool_input": {"path": ".codex/tmp/implementation-owner-attestation.yaml"}},
        )

        self.assertEqual(result.returncode, 0, result.stderr)

    def _init_repo(self) -> None:
        self._init_external_repo(self.root)

    def _init_external_repo(self, root: Path) -> None:
        subprocess.run(["git", "init", "-b", "main"], cwd=root, check=True, stdout=subprocess.DEVNULL)
        subprocess.run(["git", "config", "user.email", "codex@example.invalid"], cwd=root, check=True)
        subprocess.run(["git", "config", "user.name", "Codex"], cwd=root, check=True)
        subprocess.run(["git", "remote", "add", "origin", "https://github.com/petebeegle/homelab.git"], cwd=root, check=True)
        (root / "README.md").write_text("# test\n", encoding="utf-8")
        subprocess.run(["git", "add", "README.md"], cwd=root, check=True)
        subprocess.run(["git", "commit", "-m", "test: initialize"], cwd=root, check=True, stdout=subprocess.DEVNULL)

    def _install_harness_files(self, root: Path | None = None) -> None:
        target_root = root or self.root
        hook_path = target_root / ".codex" / "hooks" / "implementation_workflow_guard.sh"
        tool_dir = target_root / "tools" / "codex-harness"
        hook_path.parent.mkdir(parents=True, exist_ok=True)
        tool_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(HOOK_SOURCE, hook_path)
        shutil.copy2(ACTIVE_VALIDATOR, tool_dir / "validate_active_implementation.py")
        shutil.copy2(PLAN_VALIDATOR, tool_dir / "validate_implementation_plan.py")
        shutil.copy2(ATTESTATION_VALIDATOR, tool_dir / "validate_workflow_attestations.py")
        self._patch_sibling_root(
            hook_path,
            tool_dir / "validate_active_implementation.py",
            tool_dir / "validate_implementation_plan.py",
        )
        hook_path.chmod(0o755)

    def _patch_sibling_root(self, *paths: Path) -> None:
        for path in paths:
            path.write_text(
                path.read_text(encoding="utf-8").replace(
                    "/workspaces/homelab-ideas",
                    str(self.sibling_root),
                ),
                encoding="utf-8",
            )

    def _switch_to_implementation_branch(self) -> None:
        subprocess.run(
            ["git", "switch", "-c", self.branch],
            cwd=self.root,
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

    def _write_marker(self) -> None:
        tmp = self.root / ".codex" / "tmp"
        tmp.mkdir(parents=True, exist_ok=True)
        (tmp / "active-implementation").write_text(
            "\n".join(
                [
                    f"implementation={self.implementation}",
                    f"branch={self.branch}",
                    "base=origin/main",
                    "role=implementation",
                    f"clone_path={self.root}",
                    "owner_role=implementation-agent",
                    "owner_agent=implementation-agent-deterministic-role-enforcement",
                ]
            )
            + "\n",
            encoding="utf-8",
        )

    def _write_plan(self) -> None:
        tmp = self.root / ".codex" / "tmp"
        tmp.mkdir(parents=True, exist_ok=True)
        (tmp / "implementation-plan.yaml").write_text(
            "\n".join(
                [
                    f"implementation: {self.implementation}",
                    f"branch: {self.branch}",
                    "base: origin/main",
                    f"clone_path: {self.root}",
                    "owner_agent: implementation-agent-deterministic-role-enforcement",
                    "summary: Harden implementation workflow enforcement.",
                    "scope:",
                    "  - Add plan validation.",
                    "out_of_scope:",
                    "  - Live cluster changes.",
                    "planned_changes:",
                    "  - Add validator and hook checks.",
                    "docs_impact: Update ADR and runbook authority.",
                    "tests:",
                    "  - python3 -m unittest discover -s tools/codex-harness/tests",
                    "verification:",
                    "  - Harness tests pass.",
                    "risks:",
                    "  - Conservative command classification.",
                ]
            )
            + "\n",
            encoding="utf-8",
        )

    def _write_owner_attestation(self) -> None:
        tmp = self.root / ".codex" / "tmp"
        tmp.mkdir(parents=True, exist_ok=True)
        (tmp / "implementation-owner-attestation.yaml").write_text(
            "\n".join(
                [
                    f"implementation: {self.implementation}",
                    f"branch: {self.branch}",
                    "base: origin/main",
                    "role: implementation-agent",
                    "agent_id: implementation-agent-deterministic-role-enforcement",
                    f"clone_path: {self.root}",
                    "created_at: 2026-05-11T00:00:00Z",
                ]
            )
            + "\n",
            encoding="utf-8",
        )

    def _run_hook(
        self,
        arg: str | None = None,
        payload: dict[str, object] | None = None,
        cwd: Path | None = None,
    ) -> subprocess.CompletedProcess[str]:
        command = ["bash", ".codex/hooks/implementation_workflow_guard.sh"]
        if arg is not None:
            command.append(arg)
        env = os.environ.copy()
        return subprocess.run(
            command,
            cwd=cwd or self.root,
            input=json.dumps(payload or {}),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=env,
        )


if __name__ == "__main__":
    unittest.main()
