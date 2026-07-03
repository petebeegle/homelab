#!/usr/bin/env python3
"""Validate durable Spec Kit context for an active implementation."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Mapping, Sequence

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

TOOLS_LIB = Path(__file__).resolve().parents[2] / "tools" / "lib"
if str(TOOLS_LIB) not in sys.path:
    sys.path.insert(0, str(TOOLS_LIB))

from homelab_tools.git import discover_git_branch, discover_git_head, discover_git_root
from validation_common import ValidationResult, path_from_cwd
from validate_active_implementation import parse_marker, validate_marker


REQUIRED_PLAN_ARTIFACTS = ("spec.md", "plan.md", "tasks.md")
EVIDENCE_ARTIFACT = "evidence.md"
EXPLICIT_HEAD_RE = re.compile(
    r"^\s*(?:[-*]\s*)?(?:\*\*)?"
    r"(?:(?:final|verified|approved|branch|current)\s+)?head"
    r"(?:\*\*)?\s*:\s*`?([0-9a-f]{40})`?\b",
    re.IGNORECASE,
)


SddContextValidationResult = ValidationResult


def validate_sdd_context(
    *,
    root: Path | str,
    marker: Mapping[str, str],
    current_branch: str | None = None,
    require_plan_artifacts: bool = True,
    require_evidence: bool = False,
    current_head: str | None = None,
) -> SddContextValidationResult:
    errors: list[str] = []
    root_path = Path(root)

    marker_result = validate_marker(marker, current_root=root_path, current_branch=current_branch)
    errors.extend(f"Active implementation marker: {error}" for error in marker_result.errors)

    implementation = marker.get("implementation", "")
    specs_dir = root_path / "specs" / implementation if implementation else root_path / "specs" / "<implementation>"

    if require_plan_artifacts:
        for name in REQUIRED_PLAN_ARTIFACTS:
            _require_non_empty(specs_dir / name, errors)

    evidence_path = specs_dir / EVIDENCE_ARTIFACT
    if require_evidence:
        _require_non_empty(evidence_path, errors)

    if current_head and evidence_path.is_file():
        stale_heads = _stale_recorded_heads(evidence_path, current_head=current_head)
        for recorded_head in stale_heads:
            errors.append(
                f"{_display_path(root_path, evidence_path)} records HEAD {recorded_head}, "
                f"but current HEAD is {current_head}."
            )

    return SddContextValidationResult({"implementation": implementation}, tuple(errors))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate specs/<implementation>/ durable SDD context.")
    parser.add_argument("--marker", default=".codex/tmp/active-implementation")
    parser.add_argument("--root", help="Current repository root. Defaults to git rev-parse --show-toplevel.")
    parser.add_argument("--branch", help="Current branch. Defaults to git branch --show-current.")
    parser.add_argument(
        "--require-plan-artifacts",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Require non-empty spec.md, plan.md, and tasks.md.",
    )
    parser.add_argument("--require-evidence", action="store_true", help="Require non-empty evidence.md.")
    parser.add_argument(
        "--head",
        help="Current HEAD SHA. When provided, explicit HEAD records in evidence.md must match.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    root = Path(args.root) if args.root is not None else discover_git_root(Path.cwd())
    branch = args.branch if args.branch is not None else discover_git_branch(Path.cwd())
    head = args.head if args.head is not None else discover_git_head(Path.cwd())
    marker_path = path_from_cwd(args.marker)

    if not marker_path.is_file():
        print(f"Active implementation marker not found: {marker_path}", file=sys.stderr)
        return 1

    try:
        marker = parse_marker(marker_path)
    except (OSError, ValueError) as exc:
        print(f"Active implementation marker is invalid: {exc}", file=sys.stderr)
        return 1

    result = validate_sdd_context(
        root=root,
        marker=marker,
        current_branch=branch,
        require_plan_artifacts=args.require_plan_artifacts,
        require_evidence=args.require_evidence,
        current_head=head,
    )
    if result.ok:
        return 0

    print("SDD context is invalid:", file=sys.stderr)
    for error in result.errors:
        print(f"  - {error}", file=sys.stderr)
    print(
        "\nExpected durable SDD files under specs/<implementation>/: "
        "spec.md, plan.md, tasks.md"
        + (", evidence.md." if args.require_evidence else "."),
        file=sys.stderr,
    )
    return 1


def _require_non_empty(path: Path, errors: list[str]) -> None:
    if not path.is_file():
        errors.append(f"Missing required SDD artifact: {path}.")
        return
    try:
        content = path.read_text(encoding="utf-8")
    except OSError as exc:
        errors.append(f"Unable to read required SDD artifact {path}: {exc}.")
        return
    if not content.strip():
        errors.append(f"Required SDD artifact must not be empty: {path}.")


def _stale_recorded_heads(evidence_path: Path, *, current_head: str) -> tuple[str, ...]:
    stale: list[str] = []
    try:
        lines = evidence_path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return ()

    for line in lines:
        match = EXPLICIT_HEAD_RE.match(line)
        if not match:
            continue
        recorded_head = match.group(1)
        if recorded_head != current_head:
            stale.append(recorded_head)
    return tuple(stale)


def _display_path(root: Path, path: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


if __name__ == "__main__":
    raise SystemExit(main())
