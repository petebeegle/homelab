"""Retrieval manifest parsing for context packs."""

from __future__ import annotations

from pathlib import Path

from homelab_tools.yamlish import parse_retrieval_manifest_file, strip_quotes


def parse_manifest(path: Path, index_name: str) -> dict[str, list[str]]:
    for index in parse_retrieval_manifest_file(path):
        if index.get("name") == index_name:
            return {
                "include": _string_list(index.get("include", [])),
                "exclude": _string_list(index.get("exclude", [])),
                "required_metadata": _string_list(index.get("required_metadata", [])),
            }

    raise SystemExit(f"retrieval index not found: {index_name}")


def _string_list(value: object) -> list[str]:
    if not isinstance(value, list):
        return []
    return [strip_quotes(item) for item in value if isinstance(item, str)]
