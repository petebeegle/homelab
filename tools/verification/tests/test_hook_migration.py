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


if __name__ == "__main__":
    unittest.main()
