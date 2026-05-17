from __future__ import annotations

import io
import json
import sys
import tempfile
import unittest
from pathlib import Path


TOOLS_LIB = Path(__file__).resolve().parents[1] / "lib"
if str(TOOLS_LIB) not in sys.path:
    sys.path.insert(0, str(TOOLS_LIB))

from homelab_tools.process import CommandResult, run
from homelab_tools.reporting import (
    CheckResult,
    Issue,
    format_issue_json,
    format_issue_text,
    format_issues_json,
    format_issues_text,
)
from homelab_tools.yamlish import (
    parse_frontmatter_text,
    parse_retrieval_manifest_file,
    parse_scalar_yaml_file,
    parse_simple_yaml_file,
)


class HomelabToolsTest(unittest.TestCase):
    def test_parse_simple_yaml_preserves_workflow_plan_subset(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "plan.yaml"
            path.write_text(
                "\n".join(
                    [
                        "implementation: example",
                        "scope:",
                        "  - Add shared helpers.",
                        "risks: []",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            self.assertEqual(
                parse_simple_yaml_file(path),
                {
                    "implementation": "example",
                    "scope": ["Add shared helpers."],
                    "risks": [],
                },
            )

    def test_parse_scalar_yaml_rejects_duplicate_fields(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "attestation.yaml"
            path.write_text("role: implementation-agent\nrole: verifier-agent\n", encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "duplicate field role"):
                parse_scalar_yaml_file(path)

    def test_parse_frontmatter_text_returns_body(self) -> None:
        metadata, body, errors = parse_frontmatter_text(
            "---\nstatus: \"current\"\nscope:\n  - tools\n---\n\n# Body\n",
            strip_values=True,
        )

        self.assertEqual(errors, [])
        self.assertEqual(metadata, {"status": "current", "scope": ["tools"]})
        self.assertEqual(body, "# Body")

    def test_parse_retrieval_manifest_file_preserves_index_lists(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "retrieval.yaml"
            path.write_text(
                "\n".join(
                    [
                        "---",
                        "indexes:",
                        "  - name: binding-agent-context",
                        "    include:",
                        "      - AGENTS.md",
                        "    exclude:",
                        "      - '**/secret.yaml'",
                        "    required_metadata:",
                        "      - source_path",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            self.assertEqual(
                parse_retrieval_manifest_file(path, strict=True),
                [
                    {
                        "name": "binding-agent-context",
                        "include": ["AGENTS.md"],
                        "exclude": ["**/secret.yaml"],
                        "required_metadata": ["source_path"],
                    }
                ],
            )

    def test_check_result_collects_and_reports_exit_code(self) -> None:
        result = CheckResult("example failed:")
        self.assertTrue(result.ok)

        result.add("first issue")

        self.assertFalse(result.ok)
        self.assertEqual(result.exit_code(), 1)

    def test_run_returns_captured_command_result(self) -> None:
        result = run(
            [
                sys.executable,
                "-c",
                "import sys; print(sys.stdin.read().upper())",
            ],
            input_text="hello",
        )

        self.assertIsInstance(result, CommandResult)
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "HELLO\n")
        self.assertEqual(result.stderr, "")
        self.assertEqual(result.args[:2], (sys.executable, "-c"))
        self.assertTrue(result.ok())

    def test_run_is_safe_for_non_success_codes(self) -> None:
        result = run([sys.executable, "-c", "import sys; sys.exit(7)"], success_codes=(7,))

        self.assertEqual(result.returncode, 7)
        self.assertTrue(result.ok())
        self.assertTrue(result.success)
        self.assertFalse(result.ok((0,)))

    def test_issue_text_and_json_formatting_are_stable(self) -> None:
        issue = Issue(
            path="docs/decisions/example.md",
            severity="error",
            code="ADR001",
            message="missing status",
        )

        self.assertEqual(
            format_issue_text(issue),
            "docs/decisions/example.md: error ADR001: missing status",
        )
        self.assertEqual(
            json.loads(format_issue_json(issue)),
            {
                "path": "docs/decisions/example.md",
                "severity": "error",
                "code": "ADR001",
                "message": "missing status",
            },
        )
        self.assertEqual(format_issues_text([issue]), format_issue_text(issue))
        self.assertEqual(json.loads(format_issues_json([issue])), [issue.to_dict()])

    def test_check_result_can_report_structured_issues_compatibly(self) -> None:
        stream = io.StringIO()
        result = CheckResult("example failed:")
        result.add(
            Issue(
                path="file.txt",
                severity="warning",
                code="TXT001",
                message="check me",
            )
        )

        result.print(stream=stream)

        self.assertEqual(
            stream.getvalue(),
            "example failed:\n- file.txt: warning TXT001: check me\n",
        )


if __name__ == "__main__":
    unittest.main()
