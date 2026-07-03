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
USER_PROMPT_HOOK_SOURCE = REPO_ROOT / ".codex" / "hooks" / "user_prompt_submit.sh"


class ImplementationWorkflowGuardTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmpdir = tempfile.TemporaryDirectory(prefix="guard-test-")
        self.root = Path(self.tmpdir.name)
        self.implementation = "guard-test"
        self.branch = f"codex/{self.implementation}"
        self._init_repo()
        self._install_harness_files()

    def tearDown(self) -> None:
        self.tmpdir.cleanup()

    def test_post_change_blocks_on_main(self) -> None:
        (self.root / "README.md").write_text("# changed\n", encoding="utf-8")

        result = self._run_hook()

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Current branch is main", result.stderr)

    def test_post_change_blocks_on_non_codex_branch(self) -> None:
        subprocess.run(["git", "switch", "-c", "feature/test"], cwd=self.root, check=True, stdout=subprocess.DEVNULL)
        (self.root / "README.md").write_text("# changed\n", encoding="utf-8")

        result = self._run_hook()

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("does not match codex/<implementation>", result.stderr)

    def test_post_change_allows_sdd_artifact_bootstrap(self) -> None:
        self._switch_to_implementation_branch()
        specs = self.root / "specs" / self.implementation
        specs.mkdir(parents=True, exist_ok=True)
        (specs / "spec.md").write_text("# Spec\n", encoding="utf-8")

        result = self._run_hook()

        self.assertEqual(result.returncode, 0, result.stderr)

    def test_post_change_allows_matching_branch_and_sdd_context(self) -> None:
        self._switch_to_implementation_branch()
        self._write_sdd_artifacts()
        (self.root / "README.md").write_text("# changed\n", encoding="utf-8")

        result = self._run_hook()

        self.assertEqual(result.returncode, 0, result.stderr)

    def test_post_change_blocks_without_sdd_context_after_bootstrap(self) -> None:
        self._switch_to_implementation_branch()
        self._write_sdd_artifacts()
        subprocess.run(["git", "add", "specs"], cwd=self.root, check=True)
        subprocess.run(["git", "commit", "-m", "test: add specs"], cwd=self.root, check=True, stdout=subprocess.DEVNULL)
        (self.root / "specs" / self.implementation / "tasks.md").unlink()
        (self.root / "README.md").write_text("# changed\n", encoding="utf-8")

        result = self._run_hook()

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Missing required SDD artifact", result.stderr)

    def test_preflight_bash_allows_read_only_command_on_main(self) -> None:
        result = self._run_hook("--preflight-bash", {"command": "git status --short"})

        self.assertEqual(result.returncode, 0, result.stderr)

    def test_preflight_bash_allows_default_worktree_setup_on_main(self) -> None:
        result = self._run_hook(
            "--preflight-bash",
            {
                "command": (
                    "git worktree add /workspaces/homelab-worktrees/example "
                    "-b codex/example origin/main"
                )
            },
        )

        self.assertEqual(result.returncode, 0, result.stderr)

    def test_preflight_bash_blocks_mutating_command_on_main(self) -> None:
        result = self._run_hook("--preflight-bash", {"command": "git add README.md"})

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Current branch is main", result.stderr)

    def test_preflight_bash_allows_mutating_command_with_sdd_context(self) -> None:
        self._switch_to_implementation_branch()
        self._write_sdd_artifacts()

        result = self._run_hook("--preflight-bash", {"command": "git add README.md"})

        self.assertEqual(result.returncode, 0, result.stderr)

    def test_preflight_mutation_allows_prompt_intent_marker(self) -> None:
        result = self._run_hook(
            "--preflight-mutation",
            {"tool_input": {"path": ".codex/tmp/repo-change-intent"}},
        )

        self.assertEqual(result.returncode, 0, result.stderr)

    def test_preflight_mutation_allows_sdd_artifact_bootstrap_on_codex_branch(self) -> None:
        self._switch_to_implementation_branch()

        result = self._run_hook(
            "--preflight-mutation",
            {"tool_input": {"path": f"specs/{self.implementation}/spec.md"}},
        )

        self.assertEqual(result.returncode, 0, result.stderr)

    def test_preflight_mutation_blocks_non_sdd_change_without_artifacts(self) -> None:
        self._switch_to_implementation_branch()

        result = self._run_hook("--preflight-mutation", {"tool_input": {"path": "README.md"}})

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Missing required SDD artifact", result.stderr)

    def test_user_prompt_submit_marks_repo_change_intent_and_recommends_worktree(self) -> None:
        result = self._run_prompt_hook({"prompt": "Please update the workflow harness tests."})

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("dedicated worktree", result.stdout)
        self.assertIn("/workspaces/homelab-worktrees/<implementation>", result.stdout)
        self.assertTrue((self.root / ".codex" / "tmp" / "repo-change-intent").is_file())

    def test_user_prompt_submit_ignores_read_only_prompt(self) -> None:
        result = self._run_prompt_hook({"prompt": "Please explain the workflow harness tests."})

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual("", result.stdout)
        self.assertFalse((self.root / ".codex" / "tmp" / "repo-change-intent").exists())

    def test_user_prompt_submit_ignores_review_of_change_prompt(self) -> None:
        prompts = [
            "Please review the fix in the code before approval.",
            "Please review the update to the workflow docs.",
            "Please inspect the change in the harness tests.",
        ]

        for prompt in prompts:
            with self.subTest(prompt=prompt):
                result = self._run_prompt_hook({"prompt": prompt})

                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual("", result.stdout)
                self.assertFalse((self.root / ".codex" / "tmp" / "repo-change-intent").exists())

    def _init_repo(self) -> None:
        subprocess.run(["git", "init", "-b", "main"], cwd=self.root, check=True, stdout=subprocess.DEVNULL)
        subprocess.run(["git", "config", "user.email", "codex@example.invalid"], cwd=self.root, check=True)
        subprocess.run(["git", "config", "user.name", "Codex"], cwd=self.root, check=True)
        subprocess.run(["git", "remote", "add", "origin", "https://github.com/petebeegle/homelab.git"], cwd=self.root, check=True)
        (self.root / "README.md").write_text("# test\n", encoding="utf-8")
        subprocess.run(["git", "add", "README.md"], cwd=self.root, check=True)
        subprocess.run(["git", "commit", "-m", "test: initialize"], cwd=self.root, check=True, stdout=subprocess.DEVNULL)

    def _install_harness_files(self) -> None:
        hook_path = self.root / ".codex" / "hooks" / "implementation_workflow_guard.sh"
        prompt_hook_path = self.root / ".codex" / "hooks" / "user_prompt_submit.sh"
        hook_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(HOOK_SOURCE, hook_path)
        shutil.copy2(USER_PROMPT_HOOK_SOURCE, prompt_hook_path)
        hook_path.chmod(0o755)
        prompt_hook_path.chmod(0o755)

    def _switch_to_implementation_branch(self) -> None:
        subprocess.run(
            ["git", "switch", "-c", self.branch],
            cwd=self.root,
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

    def _write_sdd_artifacts(self) -> None:
        specs = self.root / "specs" / self.implementation
        specs.mkdir(parents=True, exist_ok=True)
        (specs / "spec.md").write_text("# Spec\n", encoding="utf-8")
        (specs / "plan.md").write_text("# Plan\n", encoding="utf-8")
        (specs / "tasks.md").write_text("# Tasks\n", encoding="utf-8")
        (specs / "evidence.md").write_text("# Evidence\n", encoding="utf-8")

    def _run_hook(
        self,
        arg: str | None = None,
        payload: dict[str, object] | None = None,
    ) -> subprocess.CompletedProcess[str]:
        command = ["bash", ".codex/hooks/implementation_workflow_guard.sh"]
        if arg is not None:
            command.append(arg)
        env = os.environ.copy()
        return subprocess.run(
            command,
            cwd=self.root,
            input=json.dumps(payload or {}),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=env,
        )

    def _run_prompt_hook(self, payload: dict[str, object]) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["bash", ".codex/hooks/user_prompt_submit.sh"],
            cwd=self.root,
            input=json.dumps(payload),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )


if __name__ == "__main__":
    unittest.main()
