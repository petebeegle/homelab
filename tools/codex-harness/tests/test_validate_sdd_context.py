from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
HARNESS_ROOT = REPO_ROOT / "tools" / "codex-harness"
if str(HARNESS_ROOT) not in sys.path:
    sys.path.insert(0, str(HARNESS_ROOT))

import validate_active_implementation
from validate_active_implementation import parse_marker
from validate_sdd_context import validate_sdd_context


class ValidateSddContextTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_parent = tempfile.TemporaryDirectory(prefix="sdd-root-")
        self.sibling_root = Path(self.temp_parent.name) / "homelab-ideas"
        self.sibling_root.mkdir()
        self.root = self.sibling_root / "sdd-context-test"
        self.root.mkdir()
        self.implementation = "sdd-context-test"
        self.branch = f"codex/{self.implementation}"
        self.original_sibling_root = validate_active_implementation.SIBLING_CLONE_ROOT
        validate_active_implementation.SIBLING_CLONE_ROOT = self.sibling_root
        self._write_marker()

    def tearDown(self) -> None:
        validate_active_implementation.SIBLING_CLONE_ROOT = self.original_sibling_root
        self.temp_parent.cleanup()

    def test_allows_valid_plan_artifacts_and_evidence(self) -> None:
        self._write_sdd_artifacts(final_head="1" * 40)

        result = self._validate(require_evidence=True, current_head="1" * 40)

        self.assertTrue(result.ok, result.errors)

    def test_blocks_missing_plan_artifact(self) -> None:
        self._write_sdd_artifacts()
        (self.root / "specs" / self.implementation / "tasks.md").unlink()

        result = self._validate()

        self.assertFalse(result.ok)
        self.assertTrue(any("Missing required SDD artifact" in error for error in result.errors))

    def test_blocks_empty_plan_artifact(self) -> None:
        self._write_sdd_artifacts()
        (self.root / "specs" / self.implementation / "plan.md").write_text("", encoding="utf-8")

        result = self._validate()

        self.assertFalse(result.ok)
        self.assertTrue(any("must not be empty" in error for error in result.errors))

    def test_blocks_missing_evidence_when_required(self) -> None:
        self._write_sdd_artifacts(include_evidence=False)

        result = self._validate(require_evidence=True)

        self.assertFalse(result.ok)
        self.assertTrue(any("evidence.md" in error for error in result.errors))

    def test_blocks_stale_evidence_head(self) -> None:
        self._write_sdd_artifacts(final_head="0" * 40)

        result = self._validate(require_evidence=True, current_head="1" * 40)

        self.assertFalse(result.ok)
        self.assertTrue(any("records HEAD" in error for error in result.errors))

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
                    "owner_agent=implementation-agent-sdd-context-test",
                ]
            )
            + "\n",
            encoding="utf-8",
        )

    def _write_sdd_artifacts(self, *, include_evidence: bool = True, final_head: str | None = None) -> None:
        specs = self.root / "specs" / self.implementation
        specs.mkdir(parents=True, exist_ok=True)
        (specs / "spec.md").write_text("# Spec\n", encoding="utf-8")
        (specs / "plan.md").write_text("# Plan\n", encoding="utf-8")
        (specs / "tasks.md").write_text("# Tasks\n", encoding="utf-8")
        if include_evidence:
            lines = ["# Evidence"]
            if final_head is not None:
                lines.append(f"- Final HEAD: {final_head}")
            (specs / "evidence.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    def _validate(self, *, require_evidence: bool = False, current_head: str | None = None):
        marker = parse_marker(self.root / ".codex" / "tmp" / "active-implementation")
        return validate_sdd_context(
            root=self.root,
            marker=marker,
            current_branch=self.branch,
            require_evidence=require_evidence,
            current_head=current_head,
        )


if __name__ == "__main__":
    unittest.main()
