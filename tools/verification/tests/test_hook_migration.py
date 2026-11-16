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
        self.assertTrue(any("implementation_workflow_guard.sh" in cmd for cmd in commands))

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
        for name in ("flux_reminder.sh", "pre_commit_check.sh", "stop_self_verify.sh"):
            self.assertFalse(any(name in cmd for cmd in commands), f"{name} is still wired")
            self.assertFalse((ROOT / ".codex/hooks" / name).exists(), f"{name} still exists")

    def test_every_wired_hook_script_exists(self):
        import re

        for cmd in self._all_hook_commands():
            for relative in re.findall(r"\$root/(\.codex/(?:hooks|scripts)/[\w.-]+)", cmd):
                self.assertTrue((ROOT / relative).exists(), f"config.toml wires missing script {relative}")


if __name__ == "__main__":
    unittest.main()
