#!/usr/bin/env python3
"""Validate decision-record frontmatter."""

from __future__ import annotations

import re
import sys
from datetime import date
from pathlib import Path

TOOLS_LIB = Path(__file__).resolve().parents[2] / "tools" / "lib"
if str(TOOLS_LIB) not in sys.path:
    sys.path.insert(0, str(TOOLS_LIB))

from homelab_tools.reporting import CheckResult
from homelab_tools.yamlish import parse_frontmatter_file


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
    result = CheckResult("decision metadata check failed:")
    seen_ids: set[str] = set()

    for path in sorted(DECISION_DIR.glob("*.md")):
        metadata, parse_errors = parse_frontmatter(path)
        result.extend(f"{path.relative_to(ROOT)}: {error}" for error in parse_errors)
        if parse_errors:
            continue

        for field in REQUIRED_FIELDS:
            if field not in metadata:
                result.add(f"{path.relative_to(ROOT)}: missing required field {field}")

        decision_id = str(metadata.get("id", ""))
        if not re.fullmatch(r"ADR-\d{4}", decision_id):
            result.add(f"{path.relative_to(ROOT)}: id must match ADR-0000")
        elif decision_id in seen_ids:
            result.add(f"{path.relative_to(ROOT)}: duplicate id {decision_id}")
        seen_ids.add(decision_id)

        if metadata.get("status") not in ALLOWED_STATUS:
            result.add(f"{path.relative_to(ROOT)}: status must be one of {sorted(ALLOWED_STATUS)}")
        if metadata.get("authority") not in ALLOWED_AUTHORITY:
            result.add(f"{path.relative_to(ROOT)}: authority must be one of {sorted(ALLOWED_AUTHORITY)}")
        if not isinstance(metadata.get("scope"), list) or not metadata["scope"]:
            result.add(f"{path.relative_to(ROOT)}: scope must be a non-empty list")

        for field in ("created", "last_verified"):
            if not valid_date(str(metadata.get(field, ""))):
                result.add(f"{path.relative_to(ROOT)}: {field} must be YYYY-MM-DD")

        for field in ("supersedes", "superseded_by"):
            value = metadata.get(field)
            if value is not None and not isinstance(value, list):
                result.add(f"{path.relative_to(ROOT)}: {field} must be a list or empty")

    if not result.ok:
        result.print()
        return result.exit_code()

    return 0


def parse_frontmatter(path: Path) -> tuple[dict[str, object], list[str]]:
    return parse_frontmatter_file(path)


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
