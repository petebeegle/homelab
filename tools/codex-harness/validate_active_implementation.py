#!/usr/bin/env python3
"""Validate the active implementation marker used by Codex harness scripts."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Mapping, Sequence

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

TOOLS_LIB = Path(__file__).resolve().parents[2] / "tools" / "lib"
if str(TOOLS_LIB) not in sys.path:
    sys.path.insert(0, str(TOOLS_LIB))

from homelab_tools.git import discover_git_branch, discover_git_root
from validation_common import ValidationResult, load_marker, path_from_cwd, require_fields


REQUIRED_FIELDS = (
    "implementation",
    "branch",
    "base",
    "role",
    "clone_path",
    "owner_role",
    "owner_agent",
)
GENERIC_OWNER_AGENTS = frozenset(
    {"assistant", "codex", "main", "orchestrator", "parent", "planner", "self"}
)
SIBLING_CLONE_ROOT = Path("/workspaces/homelab-ideas")


def parse_marker(marker_path: Path) -> dict[str, str]:
    """Parse a key=value marker file."""
    return load_marker(marker_path)


def validate_marker(
    marker: Mapping[str, str],
    *,
    current_root: Path | str | None = None,
    current_branch: str | None = None,
) -> ValidationResult:
    errors: list[str] = []

    require_fields(marker, REQUIRED_FIELDS, errors)

    implementation = marker.get("implementation", "")
    branch = marker.get("branch", "")
    base = marker.get("base", "")
    role = marker.get("role", "")
    clone_path = marker.get("clone_path", "")
    owner_role = marker.get("owner_role", "")
    owner_agent = marker.get("owner_agent", "")

    if implementation == "":
        errors.append("Field 'implementation' must not be empty.")
    elif "/" in implementation or implementation in {".", ".."}:
        errors.append(
            "Field 'implementation' must be a single sibling clone name without path separators."
        )

    expected_branch = f"codex/{implementation}" if implementation else "codex/<implementation>"
    if branch != expected_branch:
        errors.append(f"Field 'branch' must be '{expected_branch}', got '{branch}'.")

    if current_branch is not None and branch != current_branch:
        errors.append(f"Field 'branch' must match current branch '{current_branch}'.")

    if base == "":
        errors.append("Field 'base' must not be empty.")

    if role != "implementation":
        errors.append("Field 'role' must be 'implementation'.")

    if owner_role != "implementation-agent":
        errors.append("Field 'owner_role' must be 'implementation-agent'.")

    normalized_owner_agent = owner_agent.strip().lower()
    if owner_agent.strip() == "":
        errors.append("Field 'owner_agent' must identify the implementation owner.")
    elif normalized_owner_agent in GENERIC_OWNER_AGENTS:
        errors.append(
            "Field 'owner_agent' must not be a generic workflow identity "
            f"({', '.join(sorted(GENERIC_OWNER_AGENTS))})."
        )

    expected_clone = SIBLING_CLONE_ROOT / implementation if implementation else None
    if expected_clone is not None and clone_path != str(expected_clone):
        errors.append(f"Field 'clone_path' must be '{expected_clone}', got '{clone_path}'.")

    if current_root is not None:
        root = Path(current_root)
        if clone_path == "":
            errors.append("Field 'clone_path' must match the current repository root.")
        elif root.resolve() != Path(clone_path).resolve():
            errors.append(
                f"Field 'clone_path' must match current repository root '{root}', got '{clone_path}'."
            )

    return ValidationResult(marker, tuple(errors))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate .codex/tmp/active-implementation for implementation clones."
    )
    parser.add_argument(
        "--marker",
        default=".codex/tmp/active-implementation",
        help="Path to the active implementation marker.",
    )
    parser.add_argument(
        "--root",
        help="Current repository root. Defaults to git rev-parse --show-toplevel when available.",
    )
    parser.add_argument(
        "--branch",
        help="Current branch. Defaults to git branch --show-current when available.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    marker_path = path_from_cwd(args.marker)

    if not marker_path.is_file():
        print(f"Active implementation marker not found: {marker_path}", file=sys.stderr)
        return 1

    try:
        marker = parse_marker(marker_path)
    except (OSError, ValueError) as exc:
        print(f"Active implementation marker is invalid: {exc}", file=sys.stderr)
        return 1

    current_root = Path(args.root) if args.root is not None else discover_git_root(Path.cwd())
    current_branch = args.branch if args.branch is not None else discover_git_branch(Path.cwd())
    result = validate_marker(marker, current_root=current_root, current_branch=current_branch)
    if result.ok:
        return 0

    print("Active implementation marker is invalid:", file=sys.stderr)
    for error in result.errors:
        print(f"  - {error}", file=sys.stderr)
    print(
        "\nExpected .codex/tmp/active-implementation fields: "
        "implementation, branch, base, role, clone_path, owner_role, owner_agent.",
        file=sys.stderr,
    )
    print(
        "Use branch=codex/<implementation>, role=implementation, "
        "owner_role=implementation-agent, and "
        "clone_path=/workspaces/homelab-ideas/<implementation>.",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
