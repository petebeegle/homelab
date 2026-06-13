from __future__ import annotations

import contextlib
import io
import json
import tempfile
import unittest
from datetime import date
from pathlib import Path

from agent_memory.cli import main
from agent_memory.lint import lint_memory_root


def write_approved_memory(root: Path, name: str = "2026-05-09-good-memory.md", **overrides: object) -> Path:
    metadata = {
        "status": "approved",
        "created": "2026-05-09",
        "last_verified": "2026-05-10",
        "review_after": "2026-05-17",
        "source": "unit-test",
        "kind": "workflow-preference",
        "scope": ["unit-test"],
        "authority": "advisory",
        "supersedes": [],
        "superseded_by": [],
    }
    metadata.update(overrides)
    frontmatter_lines = []
    for key, value in metadata.items():
        if isinstance(value, list):
            if value:
                frontmatter_lines.append(f"{key}:")
                frontmatter_lines.extend(f"  - {item}" for item in value)
            else:
                frontmatter_lines.append(f"{key}: []")
        else:
            frontmatter_lines.append(f"{key}: {value}")
    frontmatter = "\n".join(frontmatter_lines)
    path = root / "approved" / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        f"---\n{frontmatter}\n---\n\n# Good Memory\n\nUse tested memory docs.\n",
        encoding="utf-8",
    )
    return path


class MemoryLintTests(unittest.TestCase):
    def test_valid_approved_markdown_passes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_approved_memory(root)

            result = lint_memory_root(root, today=date(2026, 5, 10))

            self.assertEqual(result.exit_code, 0)
            self.assertEqual(result.issues, ())

    def test_approved_markdown_frontmatter_comments_are_ignored(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = write_approved_memory(root)
            path.write_text(
                path.read_text(encoding="utf-8").replace(
                    "---\nstatus: approved\n",
                    "---\n# frontmatter comment\nstatus: approved\n",
                ),
                encoding="utf-8",
            )

            result = lint_memory_root(root, today=date(2026, 5, 10))

            self.assertEqual(result.exit_code, 0)
            self.assertEqual(result.issues, ())

    def test_approved_markdown_empty_frontmatter_key_is_invalid(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = write_approved_memory(root)
            path.write_text(
                path.read_text(encoding="utf-8").replace(
                    "---\nstatus: approved\n",
                    "---\n: bad\nstatus: approved\n",
                ),
                encoding="utf-8",
            )

            result = lint_memory_root(root, today=date(2026, 5, 10))

            self.assertEqual(result.exit_code, 1)
            self.assertIn("frontmatter-invalid", {issue.code for issue in result.issues})
            self.assertIn("line 1: key must not be empty", {issue.message for issue in result.issues})

    def test_invalid_approved_markdown_reports_errors(self):
        cases = {
            "missing-frontmatter.md": "# Missing Frontmatter\n\nBody.\n",
            "bad-date.md": "---\nstatus: approved\ncreated: 2026/05/09\nlast_verified: 2026-05-10\nreview_after: 2026-05-17\nsource: unit-test\nkind: note\nscope:\n  - unit-test\nauthority: advisory\nsupersedes: []\nsuperseded_by: []\n---\n\n# Bad Date\n\nBody.\n",
            "wrong-status.md": "---\nstatus: draft\ncreated: 2026-05-09\nlast_verified: 2026-05-10\nreview_after: 2026-05-17\nsource: unit-test\nkind: note\nscope:\n  - unit-test\nauthority: advisory\nsupersedes: []\nsuperseded_by: []\n---\n\n# Wrong Status\n\nBody.\n",
            "missing-h1.md": "---\nstatus: approved\ncreated: 2026-05-09\nlast_verified: 2026-05-10\nreview_after: 2026-05-17\nsource: unit-test\nkind: note\nscope:\n  - unit-test\nauthority: advisory\nsupersedes: []\nsuperseded_by: []\n---\n\nBody.\n",
            "empty-body.md": "---\nstatus: approved\ncreated: 2026-05-09\nlast_verified: 2026-05-10\nreview_after: 2026-05-17\nsource: unit-test\nkind: note\nscope:\n  - unit-test\nauthority: advisory\nsupersedes: []\nsuperseded_by: []\n---\n",
            "secret.md": "---\nstatus: approved\ncreated: 2026-05-09\nlast_verified: 2026-05-10\nreview_after: 2026-05-17\nsource: unit-test\nkind: note\nscope:\n  - unit-test\nauthority: advisory\nsupersedes: []\nsuperseded_by: []\n---\n\n# Secret\n\napi_key = supersecretvalue123\n",
        }
        expected_codes = {
            "frontmatter-missing",
            "created-invalid",
            "status-invalid",
            "heading-h1-count",
            "body-empty",
            "secret-like-content",
        }

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            approved = root / "approved"
            approved.mkdir(parents=True)
            for name, content in cases.items():
                (approved / name).write_text(content, encoding="utf-8")

            result = lint_memory_root(root, today=date(2026, 5, 10))

            self.assertEqual(result.exit_code, 1)
            self.assertTrue(expected_codes.issubset({issue.code for issue in result.issues}))

    def test_invalid_json_artifact_reports_error(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = root / "checkpoints" / "bad.json"
            path.parent.mkdir(parents=True)
            path.write_text("{not-json", encoding="utf-8")

            result = lint_memory_root(root)

            self.assertEqual(result.exit_code, 1)
            self.assertIn("json-invalid", {issue.code for issue in result.issues})

    def test_jsonl_record_required_fields_are_checked(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = root / "candidates" / "pending.jsonl"
            path.parent.mkdir(parents=True)
            path.write_text(json.dumps({"candidate_id": "one", "text": "Remember this."}) + "\n", encoding="utf-8")

            result = lint_memory_root(root)

            self.assertEqual(result.exit_code, 1)
            self.assertEqual({issue.code for issue in result.issues}, {"record-required"})

    def test_stale_approved_memory_warns_without_failure_by_default(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_approved_memory(root, name="2026-01-01-old-memory.md", created="2026-01-01")

            result = lint_memory_root(root, today=date(2026, 5, 10))

            self.assertEqual(result.exit_code, 0)
            self.assertIn("freshness-review", {issue.code for issue in result.issues})
            self.assertEqual(result.warning_count, 1)

    def test_review_overdue_warns_without_failure_by_default(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_approved_memory(root, review_after="2026-05-09")

            result = lint_memory_root(root, today=date(2026, 5, 10))

            self.assertEqual(result.exit_code, 0)
            self.assertIn("review-overdue", {issue.code for issue in result.issues})
            self.assertEqual(result.warning_count, 1)

    def test_invalid_supersession_metadata_reports_errors(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_approved_memory(root, last_verified="2026-05-08", authority="policy", scope=[])

            result = lint_memory_root(root, today=date(2026, 5, 10))

            self.assertEqual(result.exit_code, 1)
            self.assertTrue(
                {"last-verified-invalid", "authority-invalid", "scope-invalid"}.issubset(
                    {issue.code for issue in result.issues}
                )
            )

    def test_strict_fails_when_warnings_exist(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_approved_memory(root, name="2026-01-01-old-memory.md", created="2026-01-01")

            result = lint_memory_root(root, strict=True, today=date(2026, 5, 10))

            self.assertEqual(result.exit_code, 1)
            self.assertEqual(result.error_count, 0)
            self.assertEqual(result.warning_count, 1)

    def test_cli_json_output_contains_issue_shape(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_approved_memory(root, source="unknown", review_after="2999-01-01")
            stdout = io.StringIO()

            with contextlib.redirect_stdout(stdout):
                exit_code = main(
                    ["lint", "--root", str(root), "--format", "json", "--review-window-days", "999999"]
                )

            payload = json.loads(stdout.getvalue())
            self.assertEqual(exit_code, 0)
            self.assertEqual(payload["warnings"], 1)
            self.assertEqual(payload["issues"][0]["severity"], "warning")
            self.assertEqual(payload["issues"][0]["code"], "frontmatter-vague")
            self.assertIn("path", payload["issues"][0])
            self.assertIn("message", payload["issues"][0])
