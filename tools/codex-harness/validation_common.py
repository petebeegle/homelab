"""Shared helpers for Codex workflow validation CLIs."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Mapping, Sequence


TOOLS_LIB = Path(__file__).resolve().parents[2] / "tools" / "lib"
if str(TOOLS_LIB) not in sys.path:
    sys.path.insert(0, str(TOOLS_LIB))

from homelab_tools.yamlish import (
    parse_key_value_file,
    parse_scalar_yaml_file,
    parse_simple_yaml_file,
)


class ValidationResult:
    def __init__(
        self,
        values: Mapping[str, object] | None = None,
        errors: Sequence[str] = (),
        *,
        marker: Mapping[str, object] | None = None,
        plan: Mapping[str, object] | None = None,
        attestation: Mapping[str, object] | None = None,
    ) -> None:
        selected = values
        for candidate in (marker, plan, attestation):
            if selected is None and candidate is not None:
                selected = candidate
        self.values = selected or {}
        self.errors = tuple(errors)

    @property
    def ok(self) -> bool:
        return not self.errors

    @property
    def marker(self) -> Mapping[str, object]:
        return self.values

    @property
    def plan(self) -> Mapping[str, object]:
        return self.values

    @property
    def attestation(self) -> Mapping[str, object]:
        return self.values


def require_fields(values: Mapping[str, object], fields: Sequence[str], errors: list[str]) -> None:
    for field in fields:
        if field not in values:
            errors.append(f"Missing required field '{field}'.")


def path_from_cwd(value: str, *, cwd: Path | None = None) -> Path:
    path = Path(value)
    if path.is_absolute():
        return path
    return (cwd or Path.cwd()) / path


def resolve_repo_relative_path(
    root: Path | str,
    value: str,
    *,
    required_parent: Path | str | None = None,
) -> Path | None:
    path = Path(value)
    if path.is_absolute():
        return None

    repo_root = Path(root)
    resolved = (repo_root / path).resolve(strict=False)
    if required_parent is None:
        return resolved

    parent = (repo_root / required_parent).resolve(strict=False)
    try:
        resolved.relative_to(parent)
    except ValueError:
        return None
    return resolved


def load_marker(path: Path) -> dict[str, str]:
    return parse_key_value_file(path, quote_chars='"')


def load_plan(path: Path) -> dict[str, object]:
    return parse_simple_yaml_file(path)


def load_scalar_yaml(path: Path) -> dict[str, str]:
    return parse_scalar_yaml_file(path)
