"""Issue collection and stderr reporting helpers."""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, TextIO


@dataclass(frozen=True)
class Issue:
    """Structured issue for stable text and JSON reports."""

    path: str
    severity: str
    code: str
    message: str

    @classmethod
    def from_parts(
        cls,
        *,
        path: str | Path,
        severity: str,
        code: str,
        message: str,
    ) -> "Issue":
        return cls(path=str(path), severity=severity, code=code, message=message)

    def to_dict(self) -> dict[str, str]:
        return {
            "path": self.path,
            "severity": self.severity,
            "code": self.code,
            "message": self.message,
        }


def format_issue_text(issue: Issue) -> str:
    return f"{issue.path}: {issue.severity} {issue.code}: {issue.message}"


def format_issues_text(issues: Iterable[Issue]) -> str:
    return "\n".join(format_issue_text(issue) for issue in issues)


def format_issue_json(issue: Issue) -> str:
    return json.dumps(issue.to_dict(), sort_keys=True, separators=(",", ":"))


def format_issues_json(issues: Iterable[Issue]) -> str:
    return json.dumps(
        [issue.to_dict() for issue in issues],
        sort_keys=True,
        separators=(",", ":"),
    )


@dataclass
class CheckResult:
    """Mutable issue collector for small CLI policy checks."""

    title: str | None = None
    issues: list[str | Issue] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.issues

    def add(self, issue: str | Issue) -> None:
        self.issues.append(issue)

    def extend(self, issues: Iterable[str | Issue]) -> None:
        self.issues.extend(issues)

    def print(self, *, stream: TextIO = sys.stderr, bullet: str = "- ") -> None:
        if self.title:
            print(self.title, file=stream)
        for issue in self.issues:
            text = format_issue_text(issue) if isinstance(issue, Issue) else issue
            print(f"{bullet}{text}" if bullet else text, file=stream)

    def exit_code(self) -> int:
        return 0 if self.ok else 1
