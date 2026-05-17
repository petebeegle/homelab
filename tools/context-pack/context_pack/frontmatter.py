"""Frontmatter helpers for context-pack source filtering."""

from __future__ import annotations

from datetime import date

from homelab_tools.yamlish import parse_frontmatter_text, strip_quotes


def split_frontmatter(text: str) -> tuple[dict[str, object], str]:
    metadata, body, errors = parse_frontmatter_text(text, strip_values=True)
    if errors and (
        "missing opening frontmatter marker" in errors
        or "missing closing frontmatter marker" in errors
    ):
        return {}, text
    return metadata, body


def is_inactive(metadata: dict[str, object], today: date) -> bool:
    superseded_by = metadata.get("superseded_by")
    if isinstance(superseded_by, list) and superseded_by:
        return True

    review_after = metadata.get("review_after")
    if isinstance(review_after, str):
        try:
            return today > date.fromisoformat(strip_quotes(review_after))
        except ValueError:
            return False
    return False
