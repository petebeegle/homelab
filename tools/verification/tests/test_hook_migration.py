import pathlib
import tomllib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[3]


class HookMigrationContractTests(unittest.TestCase):
    def test_precommit_is_ci_authoritative_not_post_tool(self):
        config = tomllib.loads((ROOT / ".codex/config.toml").read_text())
        hooks = config["hooks"]["PostToolUse"]
        commands = [
            item["command"]
            for group in hooks
            for item in group.get("hooks", [])
        ]
        self.assertFalse(any("pre_commit_check.sh" in cmd for cmd in commands))
        self.assertTrue(any("sops_guard.sh" in cmd for cmd in commands))

        ci = (ROOT / ".github/workflows/ci.yml").read_text()
        self.assertIn("pre-commit run --all-files", ci)
        self.assertIn("pull_request:", ci)
        self.assertIn("branches:", ci)
        self.assertIn("- main", ci)

    def _all_hook_commands(self):
        config = tomllib.loads((ROOT / ".codex/config.toml").read_text())
        return [
            item["command"]
            for groups in config["hooks"].values()
            for group in groups
            for item in group.get("hooks", [])
        ]

    def test_removed_hooks_are_neither_wired_nor_present(self):
        commands = self._all_hook_commands()
        for name in (
            "flux_reminder.sh",
            "pre_commit_check.sh",
            "stop_self_verify.sh",
            # docs/decisions.md (changes): no hook or push guard may require per-PR Spec Kit artifacts.
            "implementation_workflow_guard.sh",
            "verifier_push_guard.sh",
            "user_prompt_submit.sh",
        ):
            self.assertFalse(any(name in cmd for cmd in commands), f"{name} is still wired")
            self.assertFalse((ROOT / ".codex/hooks" / name).exists(), f"{name} still exists")

    def test_the_two_safety_guards_stay_wired(self):
        commands = self._all_hook_commands()
        for name in ("sops_guard.sh", "terraform_plan.sh"):
            self.assertTrue(any(name in cmd for cmd in commands), f"{name} must stay wired (docs/decisions.md)")
            self.assertTrue((ROOT / ".codex/hooks" / name).exists())

    def test_nothing_requires_spec_kit_artifacts_before_a_push(self):
        precommit = (ROOT / ".pre-commit-config.yaml").read_text()
        self.assertNotIn("spec-kit-push-guard", precommit)
        self.assertNotIn("pre-push", precommit)
        self.assertFalse(any("create_implementation_pr" in cmd for cmd in self._all_hook_commands()))
        for path in (".specify", ".agents/skills"):
            self.assertFalse((ROOT / path).exists(), f"{path} still exists")

    def test_hooks_run_directly_without_the_telemetry_wrapper(self):
        # The Codex operations dashboard is gone, so nothing consumes hook telemetry.
        self.assertFalse(any("codex_observe" in cmd for cmd in self._all_hook_commands()))
        self.assertFalse((ROOT / ".codex/scripts/codex_observe.py").exists())

    def _claude_hook_commands(self):
        import json

        settings = json.loads((ROOT / ".claude/settings.json").read_text())
        return [
            item["command"]
            for groups in settings.get("hooks", {}).values()
            for group in groups
            for item in group.get("hooks", [])
        ]

    def test_claude_uses_the_same_two_guard_scripts_and_nothing_else(self):
        import re

        commands = self._claude_hook_commands()
        self.assertFalse((ROOT / ".claude/hooks").exists(), ".claude/hooks duplicates .codex/hooks")
        scripts = sorted(
            name for cmd in commands for name in re.findall(r"\.codex/hooks/([\w.-]+)", cmd)
        )
        self.assertEqual(scripts, ["sops_guard.sh", "terraform_plan.sh"])
        self.assertEqual(len(commands), 2, f"unexpected extra Claude hooks: {commands}")
        for cmd in commands:
            # Claude Code only blocks a tool call on exit code 2.
            self.assertIn("|| exit 2", cmd)

    def test_every_wired_hook_script_exists(self):
        import re

        for cmd in self._all_hook_commands():
            for relative in re.findall(r"\$root/(\.codex/(?:hooks|scripts)/[\w.-]+)", cmd):
                self.assertTrue((ROOT / relative).exists(), f"config.toml wires missing script {relative}")


if __name__ == "__main__":
    unittest.main()
