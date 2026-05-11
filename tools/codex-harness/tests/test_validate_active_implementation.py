from __future__ import annotations

import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[1] / "validate_active_implementation.py"
SPEC = importlib.util.spec_from_file_location("validate_active_implementation", MODULE_PATH)
assert SPEC is not None
validator = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = validator
SPEC.loader.exec_module(validator)


def valid_marker() -> dict[str, str]:
    implementation = "deterministic-implementation-ownership"
    return {
        "implementation": implementation,
        "branch": f"codex/{implementation}",
        "base": "origin/main",
        "role": "implementation",
        "clone_path": f"/workspaces/homelab-ideas/{implementation}",
        "owner_role": "implementation-agent",
        "owner_agent": "implementation-agent-deterministic-role-enforcement",
    }


class ValidateMarkerTest(unittest.TestCase):
    def assert_invalid_contains(self, marker: dict[str, str], expected: str) -> None:
        result = validator.validate_marker(marker)
        self.assertFalse(result.ok)
        self.assertIn(expected, "\n".join(result.errors))

    def test_valid_marker(self) -> None:
        marker = valid_marker()
        result = validator.validate_marker(
            marker,
            current_root=marker["clone_path"],
            current_branch=marker["branch"],
        )
        self.assertTrue(result.ok, result.errors)

    def test_missing_fields(self) -> None:
        marker = valid_marker()
        marker.pop("owner_agent")
        self.assert_invalid_contains(marker, "Missing required field 'owner_agent'.")

    def test_branch_mismatch(self) -> None:
        marker = valid_marker()
        marker["branch"] = "codex/other"
        self.assert_invalid_contains(
            marker,
            "Field 'branch' must be 'codex/deterministic-implementation-ownership'",
        )

    def test_wrong_clone_path(self) -> None:
        marker = valid_marker()
        marker["clone_path"] = "/workspaces/homelab"
        self.assert_invalid_contains(
            marker,
            "Field 'clone_path' must be '/workspaces/homelab-ideas/deterministic-implementation-ownership'",
        )

    def test_wrong_owner_role(self) -> None:
        marker = valid_marker()
        marker["owner_role"] = "planner"
        self.assert_invalid_contains(
            marker,
            "Field 'owner_role' must be 'implementation-agent'.",
        )

    def test_empty_owner(self) -> None:
        marker = valid_marker()
        marker["owner_agent"] = ""
        self.assert_invalid_contains(
            marker,
            "Field 'owner_agent' must identify the implementation owner.",
        )

    def test_generic_owner_values(self) -> None:
        for owner_agent in ("codex", "assistant", "planner", "parent", "main", "self", "orchestrator"):
            with self.subTest(owner_agent=owner_agent):
                marker = valid_marker()
                marker["owner_agent"] = owner_agent
                self.assert_invalid_contains(
                    marker,
                    "Field 'owner_agent' must not be a generic workflow identity",
                )

    def test_cli_reports_invalid_marker(self) -> None:
        marker = valid_marker()
        marker["owner_agent"] = "planner"
        with tempfile.TemporaryDirectory() as tmpdir:
            marker_path = Path(tmpdir) / "active-implementation"
            marker_path.write_text(
                "\n".join(f"{key}={value}" for key, value in marker.items()) + "\n",
                encoding="utf-8",
            )
            result = subprocess.run(
                [
                    sys.executable,
                    str(MODULE_PATH),
                    "--marker",
                    str(marker_path),
                    "--root",
                    marker["clone_path"],
                    "--branch",
                    marker["branch"],
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Active implementation marker is invalid", result.stderr)
        self.assertIn("owner_agent", result.stderr)


if __name__ == "__main__":
    unittest.main()
