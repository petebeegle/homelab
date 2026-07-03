#!/usr/bin/env python3
"""Validate exact mirrors for shared synthetic smoke files."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Sequence

TOOLS_LIB = Path(__file__).resolve().parents[2] / "tools" / "lib"
if str(TOOLS_LIB) not in sys.path:
    sys.path.insert(0, str(TOOLS_LIB))

from homelab_tools.reporting import CheckResult


ROOT = Path(__file__).resolve().parents[2]
MIRRORED_FILE_PAIRS = (
    (
        Path("tests/smoke/routes.spec.js"),
        Path("kubernetes/apps/synthetics/smoke/routes.spec.js"),
    ),
    (
        Path("tests/smoke/package-lock.json"),
        Path("kubernetes/apps/synthetics/smoke/package-lock.json"),
    ),
)


def check_mirrors(root: Path) -> CheckResult:
    result = CheckResult("Synthetic smoke mirror check failed:")
    for left, right in MIRRORED_FILE_PAIRS:
        result.extend(compare_pair(root, left, right))
    return result


def compare_pair(root: Path, left: Path, right: Path) -> list[str]:
    left_path = root / left
    right_path = root / right
    issues: list[str] = []

    if not left_path.is_file():
        issues.append(f"{left} is missing")
    if not right_path.is_file():
        issues.append(f"{right} is missing")
    if issues:
        return issues

    if left_path.read_bytes() != right_path.read_bytes():
        issues.append(
            f"{left} must exactly match {right}; update both shared smoke copies together"
        )
    return issues


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Check that required local and in-cluster synthetic smoke files are exact mirrors."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=ROOT,
        help="Repository root. Defaults to the root containing this script.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    result = check_mirrors(args.root)
    if not result.ok:
        result.print(stream=sys.stderr)
    return result.exit_code()


if __name__ == "__main__":
    raise SystemExit(main())
