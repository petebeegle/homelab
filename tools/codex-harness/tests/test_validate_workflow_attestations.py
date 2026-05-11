from __future__ import annotations

import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[1] / "validate_workflow_attestations.py"
sys.path.insert(0, str(MODULE_PATH.parent))
SPEC = importlib.util.spec_from_file_location("validate_workflow_attestations", MODULE_PATH)
assert SPEC is not None
validator = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = validator
SPEC.loader.exec_module(validator)


def marker() -> dict[str, str]:
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


def plan() -> dict[str, object]:
    values = marker()
    return {
        "implementation": values["implementation"],
        "branch": values["branch"],
        "base": values["base"],
        "clone_path": values["clone_path"],
        "owner_agent": values["owner_agent"],
    }


def owner_attestation() -> dict[str, str]:
    values = marker()
    return {
        "implementation": values["implementation"],
        "branch": values["branch"],
        "base": values["base"],
        "role": "implementation-agent",
        "agent_id": values["owner_agent"],
        "clone_path": values["clone_path"],
        "created_at": "2026-05-11T00:00:00Z",
    }


def verifier_attestation() -> dict[str, str]:
    values = owner_attestation()
    values["role"] = "verifier-agent"
    values["agent_id"] = "verifier-agent-deterministic-role-enforcement"
    values["approved_head"] = "abc123"
    return values


class ValidateWorkflowAttestationsTest(unittest.TestCase):
    def assert_owner_invalid_contains(self, attestation: dict[str, str], expected: str) -> None:
        result = validator.validate_owner_attestation(attestation, marker=marker(), plan=plan())
        self.assertFalse(result.ok)
        self.assertIn(expected, "\n".join(result.errors))

    def assert_verifier_invalid_contains(self, attestation: dict[str, str], expected: str) -> None:
        result = validator.validate_verifier_attestation(
            attestation,
            marker=marker(),
            owner_attestation=owner_attestation(),
            current_head="abc123",
        )
        self.assertFalse(result.ok)
        self.assertIn(expected, "\n".join(result.errors))

    def test_valid_owner_attestation(self) -> None:
        result = validator.validate_owner_attestation(
            owner_attestation(),
            marker=marker(),
            plan=plan(),
            current_root=marker()["clone_path"],
            current_branch=marker()["branch"],
        )

        self.assertTrue(result.ok, result.errors)

    def test_owner_attestation_missing_field(self) -> None:
        attestation = owner_attestation()
        attestation.pop("created_at")

        self.assert_owner_invalid_contains(attestation, "Missing required field 'created_at'.")

    def test_owner_attestation_mismatch(self) -> None:
        attestation = owner_attestation()
        attestation["branch"] = "codex/other"

        self.assert_owner_invalid_contains(
            attestation,
            "Field 'branch' must match active implementation marker value",
        )

    def test_owner_attestation_rejects_generic_identity(self) -> None:
        attestation = owner_attestation()
        attestation["agent_id"] = "assistant"

        self.assert_owner_invalid_contains(
            attestation,
            "Field 'agent_id' must not be a generic workflow identity",
        )

    def test_valid_verifier_attestation(self) -> None:
        result = validator.validate_verifier_attestation(
            verifier_attestation(),
            marker=marker(),
            owner_attestation=owner_attestation(),
            current_head="abc123",
            current_root=marker()["clone_path"],
            current_branch=marker()["branch"],
        )

        self.assertTrue(result.ok, result.errors)

    def test_verifier_attestation_rejects_same_identity_as_owner(self) -> None:
        attestation = verifier_attestation()
        attestation["agent_id"] = owner_attestation()["agent_id"]

        self.assert_verifier_invalid_contains(
            attestation,
            "Field 'agent_id' must differ from implementation owner agent_id.",
        )

    def test_verifier_attestation_rejects_wrong_head(self) -> None:
        attestation = verifier_attestation()
        attestation["approved_head"] = "def456"

        self.assert_verifier_invalid_contains(
            attestation,
            "Field 'approved_head' must match current HEAD 'abc123'",
        )

    def test_parse_rejects_lists(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "attestation.yaml"
            path.write_text("implementation:\n  - bad\n", encoding="utf-8")

            with self.assertRaises(ValueError):
                validator.parse_attestation(path)

    def test_cli_reports_invalid_verifier_attestation(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            marker_path = root / "active-implementation"
            owner_path = root / "implementation-owner-attestation.yaml"
            verifier_path = root / "verifier-attestation.yaml"
            marker_path.write_text(_render_marker(marker()), encoding="utf-8")
            owner_path.write_text(_render_yaml(owner_attestation()), encoding="utf-8")
            invalid_verifier = verifier_attestation()
            invalid_verifier["approved_head"] = "def456"
            verifier_path.write_text(_render_yaml(invalid_verifier), encoding="utf-8")

            result = subprocess.run(
                [
                    sys.executable,
                    str(MODULE_PATH),
                    "--kind",
                    "verifier",
                    "--attestation",
                    str(verifier_path),
                    "--marker",
                    str(marker_path),
                    "--owner-attestation",
                    str(owner_path),
                    "--head",
                    "abc123",
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Workflow verifier attestation is invalid", result.stderr)
        self.assertIn("approved_head", result.stderr)


def _render_yaml(values: dict[str, str]) -> str:
    return "\n".join(f"{key}: {value}" for key, value in values.items()) + "\n"


def _render_marker(values: dict[str, str]) -> str:
    return "\n".join(f"{key}={value}" for key, value in values.items()) + "\n"


if __name__ == "__main__":
    unittest.main()
