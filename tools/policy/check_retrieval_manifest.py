#!/usr/bin/env python3
"""Validate the Codex retrieval manifest."""

from __future__ import annotations

import sys
from pathlib import Path

TOOLS_LIB = Path(__file__).resolve().parents[2] / "tools" / "lib"
if str(TOOLS_LIB) not in sys.path:
    sys.path.insert(0, str(TOOLS_LIB))

from homelab_tools.reporting import CheckResult
from homelab_tools.yamlish import strip_quotes


ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / ".codex" / "retrieval.yaml"
REQUIRED_TOP_KEYS = {"name", "include", "exclude", "required_metadata"}
REQUIRED_EXCLUDES = {
    ".codex/tmp/**",
    ".codex/logs/**",
    ".codex/memory/candidates/**",
    ".codex/memory/checkpoints/**",
    ".codex/memory/rejected/**",
    "**/secret.yaml",
    "**/grafana-env.yaml",
    "*.tfvars",
    "**/*.tfvars",
    "*.tfstate",
    "**/*.tfstate",
    "kubeconfig",
    "**/kubeconfig",
    "talosconfig",
    "**/talosconfig",
}
REQUIRED_METADATA = {
    "source_path",
    "commit_sha",
    "kind",
    "status",
    "scope",
    "authority",
    "last_verified",
}


def main() -> int:
    result = CheckResult("retrieval manifest check failed:")
    try:
        indexes = parse_manifest(MANIFEST)
    except ValueError as error:
        result.add(str(error))
        indexes = []

    if not indexes:
        result.add("manifest must define at least one index")

    for index in indexes:
        missing = REQUIRED_TOP_KEYS - index.keys()
        if missing:
            result.add(f"{index.get('name', '<unnamed>')}: missing keys {sorted(missing)}")
            continue

        include = index["include"]
        exclude = index["exclude"]
        metadata = index["required_metadata"]

        for field, value in (("include", include), ("exclude", exclude), ("required_metadata", metadata)):
            if not isinstance(value, list) or not value:
                result.add(f"{index['name']}: {field} must be a non-empty list")

        if isinstance(include, list):
            for pattern in include:
                if not matches_repo_file(pattern):
                    result.add(f"{index['name']}: include pattern has no tracked match: {pattern}")

        if isinstance(exclude, list):
            missing_excludes = REQUIRED_EXCLUDES - set(exclude)
            if missing_excludes:
                result.add(f"{index['name']}: missing required excludes {sorted(missing_excludes)}")

        if isinstance(metadata, list):
            missing_metadata = REQUIRED_METADATA - set(metadata)
            if missing_metadata:
                result.add(f"{index['name']}: missing required metadata {sorted(missing_metadata)}")

    if not result.ok:
        result.print()
    return result.exit_code()


def parse_manifest(path: Path) -> list[dict[str, object]]:
    if not path.exists():
        raise ValueError(f"{path.relative_to(ROOT)} is missing")

    indexes: list[dict[str, object]] = []
    current: dict[str, object] | None = None
    current_list: str | None = None
    in_indexes = False

    for line_number, raw_line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        line = raw_line.split("#", 1)[0].rstrip()
        if not line.strip() or line.strip() == "---":
            continue
        if line == "indexes:":
            in_indexes = True
            continue
        if not in_indexes:
            raise ValueError(f"line {line_number}: only indexes is supported at top level")
        if line.startswith("  - name: "):
            current = {"name": line.split(":", 1)[1].strip()}
            indexes.append(current)
            current_list = None
            continue
        if current is None:
            raise ValueError(f"line {line_number}: index item must start with name")
        if line.startswith("    ") and line.endswith(":"):
            current_list = line.strip()[:-1]
            current[current_list] = []
            continue
        if line.startswith("      - ") and current_list:
            value = line.strip()[2:].strip()
            value = strip_quotes(value)
            current_value = current[current_list]
            if isinstance(current_value, list):
                current_value.append(value)
            continue
        raise ValueError(f"line {line_number}: unsupported manifest syntax")

    return indexes


def matches_repo_file(pattern: str) -> bool:
    for path in ROOT.glob(pattern):
        if path.is_file() and ".git" not in path.parts:
            return True
    return False


if __name__ == "__main__":
    raise SystemExit(main())
