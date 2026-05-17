#!/usr/bin/env python3
"""Validate the local implementation plan used by Codex harness scripts."""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping, Sequence

TOOLS_LIB = Path(__file__).resolve().parents[2] / "tools" / "lib"
if str(TOOLS_LIB) not in sys.path:
    sys.path.insert(0, str(TOOLS_LIB))

from homelab_tools.yamlish import parse_simple_yaml_file
from validate_active_implementation import parse_marker


REQUIRED_SCALAR_FIELDS = (
    "implementation",
    "branch",
    "base",
    "clone_path",
    "owner_agent",
    "summary",
    "docs_impact",
)
REQUIRED_LIST_FIELDS = (
    "scope",
    "out_of_scope",
    "planned_changes",
    "tests",
    "verification",
    "risks",
)
ALL_REQUIRED_FIELDS = REQUIRED_SCALAR_FIELDS + REQUIRED_LIST_FIELDS


@dataclass(frozen=True)
class PlanValidationResult:
    plan: Mapping[str, object]
    errors: tuple[str, ...]

    @property
    def ok(self) -> bool:
        return not self.errors


def parse_plan(plan_path: Path) -> dict[str, object]:
    """Parse the simple YAML subset used by .codex/tmp/implementation-plan.yaml."""
    return parse_simple_yaml_file(plan_path)


def validate_plan(
    plan: Mapping[str, object],
    *,
    marker: Mapping[str, str] | None = None,
    current_root: Path | str | None = None,
    current_branch: str | None = None,
) -> PlanValidationResult:
    errors: list[str] = []

    for field in ALL_REQUIRED_FIELDS:
        if field not in plan:
            errors.append(f"Missing required field '{field}'.")

    for field in REQUIRED_SCALAR_FIELDS:
        value = plan.get(field)
        if not isinstance(value, str) or not value.strip():
            errors.append(f"Field '{field}' must be a non-empty scalar.")

    for field in REQUIRED_LIST_FIELDS:
        value = plan.get(field)
        if not isinstance(value, list) or not value or not all(isinstance(item, str) and item.strip() for item in value):
            errors.append(f"Field '{field}' must be a non-empty list of strings.")

    implementation = _string(plan.get("implementation"))
    branch = _string(plan.get("branch"))
    clone_path = _string(plan.get("clone_path"))

    if implementation:
        expected_branch = f"codex/{implementation}"
        expected_clone = f"/workspaces/homelab-ideas/{implementation}"
        if branch != expected_branch:
            errors.append(f"Field 'branch' must be '{expected_branch}', got '{branch}'.")
        if clone_path != expected_clone:
            errors.append(f"Field 'clone_path' must be '{expected_clone}', got '{clone_path}'.")

    if current_branch is not None and branch and branch != current_branch:
        errors.append(f"Field 'branch' must match current branch '{current_branch}'.")

    if current_root is not None and clone_path:
        root = Path(current_root)
        if root.resolve() != Path(clone_path).resolve():
            errors.append(f"Field 'clone_path' must match current repository root '{root}', got '{clone_path}'.")

    if marker is not None:
        for field in ("implementation", "branch", "base", "clone_path", "owner_agent"):
            plan_value = _string(plan.get(field))
            marker_value = marker.get(field, "")
            if plan_value != marker_value:
                errors.append(
                    f"Field '{field}' must match active implementation marker value '{marker_value}', got '{plan_value}'."
                )

    return PlanValidationResult(plan=plan, errors=tuple(errors))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate .codex/tmp/implementation-plan.yaml.")
    parser.add_argument(
        "--plan",
        default=".codex/tmp/implementation-plan.yaml",
        help="Path to the implementation plan.",
    )
    parser.add_argument(
        "--marker",
        default=".codex/tmp/active-implementation",
        help="Path to the active implementation marker.",
    )
    parser.add_argument(
        "--root",
        help="Current repository root. Defaults to the current working directory.",
    )
    parser.add_argument(
        "--branch",
        help="Current branch. When provided, the plan branch must match.",
    )
    parser.add_argument(
        "--no-marker",
        action="store_true",
        help="Validate plan shape without cross-checking the active implementation marker.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    plan_path = Path(args.plan)
    if not plan_path.is_absolute():
        plan_path = Path.cwd() / plan_path
    if not plan_path.is_file():
        print(f"Implementation plan not found: {plan_path}", file=sys.stderr)
        return 1

    try:
        plan = parse_plan(plan_path)
    except (OSError, ValueError) as exc:
        print(f"Implementation plan is invalid: {exc}", file=sys.stderr)
        return 1

    marker = None
    if not args.no_marker:
        marker_path = Path(args.marker)
        if not marker_path.is_absolute():
            marker_path = Path.cwd() / marker_path
        if not marker_path.is_file():
            print(f"Active implementation marker not found: {marker_path}", file=sys.stderr)
            return 1
        try:
            marker = parse_marker(marker_path)
        except (OSError, ValueError) as exc:
            print(f"Active implementation marker is invalid: {exc}", file=sys.stderr)
            return 1

    result = validate_plan(
        plan,
        marker=marker,
        current_root=Path(args.root) if args.root is not None else Path.cwd(),
        current_branch=args.branch,
    )
    if result.ok:
        return 0

    print("Implementation plan is invalid:", file=sys.stderr)
    for error in result.errors:
        print(f"  - {error}", file=sys.stderr)
    print(
        "\nExpected .codex/tmp/implementation-plan.yaml fields: "
        + ", ".join(ALL_REQUIRED_FIELDS)
        + ".",
        file=sys.stderr,
    )
    return 1


def _string(value: object) -> str:
    return value if isinstance(value, str) else ""


if __name__ == "__main__":
    raise SystemExit(main())
