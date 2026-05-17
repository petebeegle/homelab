"""Parsers for the tiny YAML-like subsets used by repo-local tooling."""

from __future__ import annotations

from pathlib import Path
from typing import Any


def strip_quotes(value: str, *, quote_chars: str = "'\"") -> str:
    if len(value) >= 2 and value[0] == value[-1] and value[0] in quote_chars:
        return value[1:-1]
    return value


def parse_key_value_file(path: Path, *, quote_chars: str = '"') -> dict[str, str]:
    """Parse key=value files, preserving the harness marker error wording."""
    values: dict[str, str] = {}
    for lineno, raw_line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            raise ValueError(f"{path}:{lineno}: expected key=value, got {raw_line!r}")
        key, value = line.split("=", 1)
        key = key.strip()
        value = strip_quotes(value.strip(), quote_chars=quote_chars)
        if not key:
            raise ValueError(f"{path}:{lineno}: marker key must not be empty")
        values[key] = value
    return values


def parse_scalar_yaml_file(path: Path) -> dict[str, str]:
    """Parse a scalar-only key: value file."""
    values: dict[str, str] = {}
    for lineno, raw_line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if raw_line.startswith(" "):
            raise ValueError(f"{path}:{lineno}: unsupported indentation")
        if ":" not in raw_line:
            raise ValueError(f"{path}:{lineno}: expected key: value")

        key, raw_value = raw_line.split(":", 1)
        key = key.strip()
        value = strip_quotes(raw_value.strip())
        if not key:
            raise ValueError(f"{path}:{lineno}: key must not be empty")
        if key in values:
            raise ValueError(f"{path}:{lineno}: duplicate field {key}")
        values[key] = value
    return values


def parse_simple_yaml_file(path: Path) -> dict[str, object]:
    """Parse top-level scalars and two-space lists used by workflow plans."""
    values: dict[str, object] = {}
    current_list: str | None = None

    for lineno, raw_line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not raw_line.strip() or raw_line.lstrip().startswith("#"):
            continue

        if raw_line.startswith("  - "):
            if current_list is None:
                raise ValueError(f"{path}:{lineno}: list item without list field")
            value = strip_quotes(raw_line[4:].strip())
            if not value:
                raise ValueError(f"{path}:{lineno}: list item must not be empty")
            current_value = values[current_list]
            if not isinstance(current_value, list):
                raise ValueError(f"{path}:{lineno}: field {current_list} is not a list")
            current_value.append(value)
            continue

        current_list = None
        if raw_line.startswith(" "):
            raise ValueError(f"{path}:{lineno}: unsupported indentation")
        if ":" not in raw_line:
            raise ValueError(f"{path}:{lineno}: expected key: value")

        key, raw_value = raw_line.split(":", 1)
        key = key.strip()
        value = raw_value.strip()
        if not key:
            raise ValueError(f"{path}:{lineno}: key must not be empty")
        if key in values:
            raise ValueError(f"{path}:{lineno}: duplicate field {key}")

        if value == "":
            values[key] = []
            current_list = key
        elif value == "[]":
            values[key] = []
        else:
            values[key] = strip_quotes(value)

    return values


def parse_frontmatter_file(path: Path) -> tuple[dict[str, Any], list[str]]:
    """Parse simple Markdown frontmatter and return metadata plus parse errors."""
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0] != "---":
        return {}, ["missing opening frontmatter marker"]

    try:
        end = lines[1:].index("---") + 1
    except ValueError:
        return {}, ["missing closing frontmatter marker"]

    metadata: dict[str, Any] = {}
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
                current_value = metadata[current_list]
                if isinstance(current_value, list):
                    current_value.append(value)
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
