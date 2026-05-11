from __future__ import annotations

import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[1] / "validate_implementation_plan.py"
sys.path.insert(0, str(MODULE_PATH.parent))
SPEC = importlib.util.spec_from_file_location("validate_implementation_plan", MODULE_PATH)
assert SPEC is not None
validator = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = validator
SPEC.loader.exec_module(validator)


def valid_marker() -> dict[str, str]:
    implementation = "harden-implementation-workflow"
    return {
        "implementation": implementation,
        "branch": f"codex/{implementation}",
        "base": "origin/main",
        "role": "implementation",
        "clone_path": f"/workspaces/homelab-ideas/{implementation}",
        "owner_role": "implementation-agent",
        "owner_agent": "implementation-agent-deterministic-role-enforcement",
    }


def valid_plan() -> dict[str, object]:
    marker = valid_marker()
    return {
        "implementation": marker["implementation"],
        "branch": marker["branch"],
        "base": marker["base"],
        "clone_path": marker["clone_path"],
        "owner_agent": marker["owner_agent"],
        "summary": "Harden implementation workflow enforcement.",
        "scope": ["Add plan validation."],
        "out_of_scope": ["Live cluster changes."],
        "planned_changes": ["Add validator and hook checks."],
        "docs_impact": "Update ADR and runbook authority.",
        "tests": ["python3 -m unittest discover -s tools/codex-harness/tests"],
        "verification": ["Harness tests pass."],
        "risks": ["Conservative command classification."],
    }


class ValidateImplementationPlanTest(unittest.TestCase):
    def assert_invalid_contains(self, plan: dict[str, object], expected: str) -> None:
        result = validator.validate_plan(plan, marker=valid_marker())
        self.assertFalse(result.ok)
        self.assertIn(expected, "\n".join(result.errors))

    def test_valid_plan(self) -> None:
        marker = valid_marker()
        result = validator.validate_plan(
            valid_plan(),
            marker=marker,
            current_root=marker["clone_path"],
            current_branch=marker["branch"],
        )

        self.assertTrue(result.ok, result.errors)

    def test_missing_required_field(self) -> None:
        plan = valid_plan()
        plan.pop("docs_impact")

        self.assert_invalid_contains(plan, "Missing required field 'docs_impact'.")

    def test_list_fields_must_be_non_empty(self) -> None:
        plan = valid_plan()
        plan["tests"] = []

        self.assert_invalid_contains(plan, "Field 'tests' must be a non-empty list of strings.")

    def test_marker_mismatch_reports_field(self) -> None:
        plan = valid_plan()
        plan["owner_agent"] = "other-agent"

        self.assert_invalid_contains(
            plan,
            "Field 'owner_agent' must match active implementation marker value 'implementation-agent-deterministic-role-enforcement'",
        )

    def test_cli_reports_invalid_plan(self) -> None:
        marker = valid_marker()
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            marker_path = root / "active-implementation"
            plan_path = root / "implementation-plan.yaml"
            marker_path.write_text(
                "\n".join(f"{key}={value}" for key, value in marker.items()) + "\n",
                encoding="utf-8",
            )
            plan_path.write_text(
                "\n".join(
                    [
                        "implementation: harden-implementation-workflow",
                        "branch: codex/other",
                        "base: origin/main",
                        "clone_path: /workspaces/homelab-ideas/harden-implementation-workflow",
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

            result = subprocess.run(
                [
                    sys.executable,
                    str(MODULE_PATH),
                    "--plan",
                    str(plan_path),
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
        self.assertIn("Implementation plan is invalid", result.stderr)
        self.assertIn("branch", result.stderr)


if __name__ == "__main__":
    unittest.main()
