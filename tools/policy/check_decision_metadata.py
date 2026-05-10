#!/usr/bin/env python3
"""Validate decision-record frontmatter."""

from __future__ import annotations

import re
import sys
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DECISION_DIR = ROOT / "docs" / "decisions"
REQUIRED_FIELDS = (
    "id",
    "status",
    "scope",
    "authority",
    "created",
    "last_verified",
    "supersedes",
    "superseded_by",
)
ALLOWED_STATUS = {"accepted", "superseded", "deprecated"}
ALLOWED_AUTHORITY = {"binding", "advisory"}


def main() -> int:
    issues: list[str] = []
    seen_ids: set[str] = set()

    for path in sorted(DECISION_DIR.glob("*.md")):
        metadata, parse_errors = parse_frontmatter(path)
        issues.extend(f"{path.relative_to(ROOT)}: {error}" for error in parse_errors)
        if parse_errors:
            continue

        for field in REQUIRED_FIELDS:
            if field not in metadata:
                issues.append(f"{path.relative_to(ROOT)}: missing required field {field}")

        decision_id = str(metadata.get("id", ""))
        if not re.fullmatch(r"ADR-\d{4}", decision_id):
            issues.append(f"{path.relative_to(ROOT)}: id must match ADR-0000")
        elif decision_id in seen_ids:
            issues.append(f"{path.relative_to(ROOT)}: duplicate id {decision_id}")
        seen_ids.add(decision_id)

        if metadata.get("status") not in ALLOWED_STATUS:
            issues.append(f"{path.relative_to(ROOT)}: status must be one of {sorted(ALLOWED_STATUS)}")
        if metadata.get("authority") not in ALLOWED_AUTHORITY:
            issues.append(f"{path.relative_to(ROOT)}: authority must be one of {sorted(ALLOWED_AUTHORITY)}")
        if not isinstance(metadata.get("scope"), list) or not metadata["scope"]:
            issues.append(f"{path.relative_to(ROOT)}: scope must be a non-empty list")

        for field in ("created", "last_verified"):
            if not valid_date(str(metadata.get(field, ""))):
                issues.append(f"{path.relative_to(ROOT)}: {field} must be YYYY-MM-DD")

        for field in ("supersedes", "superseded_by"):
            value = metadata.get(field)
            if value is not None and not isinstance(value, list):
                issues.append(f"{path.relative_to(ROOT)}: {field} must be a list or empty")

    if issues:
        print("decision metadata check failed:", file=sys.stderr)
        for issue in issues:
            print(f"- {issue}", file=sys.stderr)
        return 1

    return 0


def parse_frontmatter(path: Path) -> tuple[dict[str, object], list[str]]:
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0] != "---":
        return {}, ["missing opening frontmatter marker"]

    try:
        end = lines[1:].index("---") + 1
    except ValueError:
        return {}, ["missing closing frontmatter marker"]

    metadata: dict[str, object] = {}
    errors: list[str] = []
    current_list: str | None = None

    for lineno, line in enumerate(lines[1:end], start=2):
        if not line.strip():
            continue
        if line.startswith("  - "):
            if current_list is None:
                errors.append(f"line {lineno}: list item without list key")
                continue
            value = line[4:].strip()
            if value:
                assert isinstance(metadata[current_list], list)
                metadata[current_list].append(value)
            continue
        current_list = None
        if ":" not in line:
            errors.append(f"line {lineno}: expected key: value")
            continue
        key, raw_value = line.split(":", 1)
        key = key.strip()
        value = raw_value.strip()
        if value == "[]":
            metadata[key] = []
        elif value == "":
            metadata[key] = []
            current_list = key
        else:
            metadata[key] = value

    return metadata, errors


def valid_date(value: str) -> bool:
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        return False
    try:
        date.fromisoformat(value)
    except ValueError:
        return False
    return True


if __name__ == "__main__":
    raise SystemExit(main())
