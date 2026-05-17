"""Lint Codex memory documents and artifacts."""

from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, Iterable

TOOLS_LIB = Path(__file__).resolve().parents[3] / "lib"
if str(TOOLS_LIB) not in sys.path:
    sys.path.insert(0, str(TOOLS_LIB))

from agent_memory.policy import secret_rejection_reason
from agent_memory.storage import memory_root
from homelab_tools.yamlish import parse_frontmatter_text

APPROVED_REQUIRED_FIELDS = (
    "status",
    "created",
    "last_verified",
    "review_after",
    "source",
    "kind",
    "scope",
    "authority",
    "supersedes",
    "superseded_by",
)
ALLOWED_AUTHORITY_VALUES = {"advisory", "binding"}
DEFAULT_REVIEW_WINDOW_DAYS = 30
DEFAULT_WORD_WARNING_THRESHOLD = 1200
VAGUE_METADATA_VALUES = {"", "unknown", "todo", "tbd", "none", "n/a"}


@dataclass(frozen=True)
class LintIssue:
    path: str
    severity: str
    code: str
    message: str

    def to_record(self) -> dict[str, str]:
        return {
            "path": self.path,
            "severity": self.severity,
            "code": self.code,
            "message": self.message,
        }


@dataclass(frozen=True)
class LintResult:
    issues: tuple[LintIssue, ...]
    strict: bool = False

    @property
    def error_count(self) -> int:
        return sum(1 for issue in self.issues if issue.severity == "error")

    @property
    def warning_count(self) -> int:
        return sum(1 for issue in self.issues if issue.severity == "warning")

    @property
    def exit_code(self) -> int:
        if self.error_count:
            return 1
        if self.strict and self.warning_count:
            return 1
        return 0

    def to_record(self) -> dict[str, object]:
        return {
            "errors": self.error_count,
            "warnings": self.warning_count,
            "strict": self.strict,
            "issues": [issue.to_record() for issue in self.issues],
        }


def lint_memory_root(
    root: str | Path | None = None,
    *,
    strict: bool = False,
    review_window_days: int = DEFAULT_REVIEW_WINDOW_DAYS,
    word_warning_threshold: int = DEFAULT_WORD_WARNING_THRESHOLD,
    today: date | None = None,
) -> LintResult:
    base = memory_root(root)
    current_date = today or datetime.now(timezone.utc).date()
    issues: list[LintIssue] = []

    if not base.exists():
        issues.append(_issue(base, "error", "missing-root", "memory root does not exist"))
        return LintResult(tuple(issues), strict=strict)

    for path in _iter_memory_files(base):
        if path.suffix == ".md" and _is_under(path, base / "approved"):
            issues.extend(
                _lint_approved_markdown(
                    path,
                    base,
                    review_window_days=review_window_days,
                    word_warning_threshold=word_warning_threshold,
                    today=current_date,
                )
            )
            continue
        if path.suffix == ".json":
            issues.extend(_lint_json_file(path, base))
            continue
        if path.suffix == ".jsonl":
            issues.extend(_lint_jsonl_file(path, base))

    return LintResult(tuple(issues), strict=strict)


def format_lint_text(result: LintResult) -> str:
    if not result.issues:
        return "agent-memory lint: no issues found"

    lines = [f"agent-memory lint: {result.error_count} error(s), {result.warning_count} warning(s)"]
    for issue in result.issues:
        lines.append(f"{issue.severity}: {issue.path}: {issue.code}: {issue.message}")
    return "\n".join(lines)


def format_lint_json(result: LintResult) -> str:
    return json.dumps(result.to_record(), sort_keys=True)


def _iter_memory_files(base: Path) -> Iterable[Path]:
    for path in sorted(base.rglob("*")):
        if not path.is_file():
            continue
        if path.name == ".gitkeep":
            continue
        yield path


def _lint_approved_markdown(
    path: Path,
    base: Path,
    *,
    review_window_days: int,
    word_warning_threshold: int,
    today: date,
) -> list[LintIssue]:
    issues: list[LintIssue] = []
    text = _read_text(path, base, issues)
    if text is None:
        return issues

    secret_reason = secret_rejection_reason(text)
    if secret_reason is not None:
        issues.append(_issue(path, "error", "secret-like-content", secret_reason, base))

    metadata, body, metadata_errors = parse_frontmatter_text(
        text,
        strip_values=True,
        metadata_line_start=1,
    )
    if metadata_errors == ["missing opening frontmatter marker"]:
        issues.append(
            _issue(
                path,
                "error",
                "frontmatter-missing",
                "approved Markdown memory must start with frontmatter",
                base,
            )
        )
        return issues
    if metadata_errors == ["missing closing frontmatter marker"]:
        issues.append(
            _issue(
                path,
                "error",
                "frontmatter-missing",
                "approved Markdown memory frontmatter is not closed",
                base,
            )
        )
        return issues
    issues.extend(_issue(path, "error", "frontmatter-invalid", message, base) for message in metadata_errors)

    for field_name in APPROVED_REQUIRED_FIELDS:
        if field_name not in metadata:
            issues.append(_issue(path, "error", "frontmatter-required", f"missing required field {field_name}", base))
            continue
        if _is_vague(metadata[field_name]):
            issues.append(_issue(path, "warning", "frontmatter-vague", f"{field_name} has a vague value", base))

    if metadata.get("status") != "approved":
        issues.append(_issue(path, "error", "status-invalid", "approved memory must have status: approved", base))

    created = _parse_date_field(metadata.get("created"))
    if created is None:
        issues.append(_issue(path, "error", "created-invalid", "created must be formatted as YYYY-MM-DD", base))
    else:
        if _has_dated_filename(path) and not path.name.startswith(f"{created.isoformat()}-"):
            issues.append(_issue(path, "error", "filename-date-mismatch", "filename date must match created", base))
        if (today - created).days > review_window_days:
            issues.append(
                _issue(
                    path,
                    "warning",
                    "freshness-review",
                    f"approved memory is older than {review_window_days} days",
                    base,
                )
            )

    last_verified = _parse_date_field(metadata.get("last_verified"))
    if last_verified is None:
        issues.append(
            _issue(path, "error", "last-verified-invalid", "last_verified must be formatted as YYYY-MM-DD", base)
        )
    elif created is not None and last_verified < created:
        issues.append(_issue(path, "error", "last-verified-invalid", "last_verified must be on or after created", base))

    review_after = _parse_date_field(metadata.get("review_after"))
    if review_after is None:
        issues.append(_issue(path, "error", "review-after-invalid", "review_after must be formatted as YYYY-MM-DD", base))
    elif today > review_after:
        issues.append(_issue(path, "warning", "review-overdue", "approved memory is past review_after", base))

    authority = metadata.get("authority")
    if authority not in ALLOWED_AUTHORITY_VALUES:
        issues.append(
            _issue(
                path,
                "error",
                "authority-invalid",
                f"authority must be one of {sorted(ALLOWED_AUTHORITY_VALUES)}",
                base,
            )
        )

    scope = metadata.get("scope")
    if not isinstance(scope, list) or not scope:
        issues.append(_issue(path, "error", "scope-invalid", "scope must be a non-empty list", base))

    for field_name in ("supersedes", "superseded_by"):
        value = metadata.get(field_name)
        if value is not None and not isinstance(value, list):
            issues.append(_issue(path, "error", "supersession-invalid", f"{field_name} must be a list or empty", base))

    h1_count = sum(1 for line in body.splitlines() if line.startswith("# "))
    if h1_count != 1:
        issues.append(_issue(path, "error", "heading-h1-count", "approved memory must contain exactly one H1", base))

    if not body.strip():
        issues.append(_issue(path, "error", "body-empty", "approved memory body must not be empty", base))
    elif _word_count(body) > word_warning_threshold:
        issues.append(
            _issue(
                path,
                "warning",
                "body-long",
                f"approved memory body is longer than {word_warning_threshold} words",
                base,
            )
        )

    return issues


def _lint_json_file(path: Path, base: Path) -> list[LintIssue]:
    issues: list[LintIssue] = []
    text = _read_text(path, base, issues)
    if text is None:
        return issues
    try:
        record = json.loads(text)
    except json.JSONDecodeError as error:
        return [_issue(path, "error", "json-invalid", f"invalid JSON: {error.msg}", base)]
    if not isinstance(record, dict):
        return [_issue(path, "error", "json-invalid", "JSON artifact must contain an object", base)]
    return _lint_record(path, base, record, line_number=None)


def _lint_jsonl_file(path: Path, base: Path) -> list[LintIssue]:
    issues: list[LintIssue] = []
    text = _read_text(path, base, issues)
    if text is None:
        return issues
    for index, line in enumerate(text.splitlines(), start=1):
        if not line.strip():
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError as error:
            issues.append(_issue(path, "error", "jsonl-invalid", f"line {index}: invalid JSON: {error.msg}", base))
            continue
        if not isinstance(record, dict):
            issues.append(_issue(path, "error", "jsonl-invalid", f"line {index}: record must be an object", base))
            continue
        issues.extend(_lint_record(path, base, record, line_number=index))
    return issues


def _lint_record(path: Path, base: Path, record: dict[str, Any], line_number: int | None) -> list[LintIssue]:
    required_fields: tuple[str, ...] = ()
    if _is_under(path, base / "checkpoints") and path.suffix == ".json":
        required_fields = ("checkpoint_id", "summary", "source", "created_at", "candidate_ids")
    elif path.suffix == ".jsonl" and (_is_under(path, base / "candidates") or _is_under(path, base / "approved")):
        required_fields = ("candidate_id", "text", "source", "created_at")

    if not required_fields:
        return []

    where = f"line {line_number}: " if line_number is not None else ""
    issues: list[LintIssue] = []
    for field_name in required_fields:
        if field_name not in record:
            issues.append(_issue(path, "error", "record-required", f"{where}missing required field {field_name}", base))
        elif isinstance(record[field_name], str) and _is_vague(record[field_name]):
            issues.append(_issue(path, "warning", "record-vague", f"{where}{field_name} has a vague value", base))

    text = "\n".join(str(record.get(field_name, "")) for field_name in ("text", "summary"))
    secret_reason = secret_rejection_reason(text)
    if secret_reason is not None:
        issues.append(_issue(path, "error", "secret-like-content", f"{where}{secret_reason}", base))

    return issues


def _parse_date_field(value: object) -> date | None:
    if not isinstance(value, str):
        return None
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


def _has_dated_filename(path: Path) -> bool:
    return re.match(r"^\d{4}-\d{2}-\d{2}-", path.name) is not None


def _is_vague(value: object) -> bool:
    return isinstance(value, str) and value.strip().lower() in VAGUE_METADATA_VALUES


def _word_count(text: str) -> int:
    return len(re.findall(r"\b\w+\b", text))


def _read_text(path: Path, base: Path, issues: list[LintIssue]) -> str | None:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        issues.append(_issue(path, "error", "encoding-invalid", "file must be UTF-8 text", base))
        return None


def _is_under(path: Path, directory: Path) -> bool:
    try:
        path.relative_to(directory)
    except ValueError:
        return False
    return True


def _issue(path: Path, severity: str, code: str, message: str, base: Path | None = None) -> LintIssue:
    issue_path = str(path)
    if base is not None:
        try:
            issue_path = str(path.relative_to(base.parent))
        except ValueError:
            issue_path = str(path)
    return LintIssue(path=issue_path, severity=severity, code=code, message=message)
