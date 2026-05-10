"""Small CLI for local memory scaffold operations."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from agent_memory.compaction import compact_transcript
from agent_memory.consolidation import consolidate_candidates, load_reviewed_candidates
from agent_memory.lint import (
    DEFAULT_REVIEW_WINDOW_DAYS,
    DEFAULT_WORD_WARNING_THRESHOLD,
    format_lint_json,
    format_lint_text,
    lint_memory_root,
)
from agent_memory.storage import ensure_memory_tree


def _read_text(path: str | None) -> str:
    if path is None or path == "-":
        return sys.stdin.read()
    return Path(path).read_text(encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="agent-memory")
    parser.add_argument("--root", default=None, help="Memory root, defaults to .codex/memory")
    subparsers = parser.add_subparsers(dest="command", required=True)

    init = subparsers.add_parser("init", help="Create memory directories with .gitkeep placeholders")
    init.add_argument("--root", default=argparse.SUPPRESS, help="Memory root, defaults to .codex/memory")

    compact = subparsers.add_parser("compact", help="Compact transcript text and checkpoint candidates")
    compact.add_argument("--root", default=argparse.SUPPRESS, help="Memory root, defaults to .codex/memory")
    compact.add_argument("path", nargs="?", default="-", help="Transcript path, or stdin when omitted")
    compact.add_argument("--source", default="transcript")

    consolidate = subparsers.add_parser("consolidate", help="Consolidate reviewed candidates")
    consolidate.add_argument("--root", default=argparse.SUPPRESS, help="Memory root, defaults to .codex/memory")
    consolidate.add_argument("--apply-reviewed", action="store_true", help="Write reviewed candidates to durable memory")

    lint = subparsers.add_parser("lint", help="Lint Codex memory docs and artifacts")
    lint.add_argument("--root", default=argparse.SUPPRESS, help="Memory root, defaults to .codex/memory")
    lint.add_argument("--strict", action="store_true", help="Treat warnings as failures")
    lint.add_argument("--format", choices=("text", "json"), default="text", help="Output format")
    lint.add_argument(
        "--review-window-days",
        type=int,
        default=DEFAULT_REVIEW_WINDOW_DAYS,
        help="Warn when approved memory is older than this many days",
    )
    lint.add_argument(
        "--word-warning-threshold",
        type=int,
        default=DEFAULT_WORD_WARNING_THRESHOLD,
        help="Warn when approved memory body exceeds this word count",
    )

    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "init":
        root = ensure_memory_tree(args.root)
        print(json.dumps({"memory_root": str(root)}))
        return 0
    if args.command == "compact":
        checkpoint = compact_transcript(_read_text(args.path), root=args.root, source=args.source)
        print(json.dumps(checkpoint.to_record(), sort_keys=True))
        return 0
    if args.command == "consolidate":
        candidates = load_reviewed_candidates(args.root)
        plan = consolidate_candidates(candidates, root=args.root, dry_run=not args.apply_reviewed)
        print(json.dumps(plan.to_record(), sort_keys=True))
        return 0
    if args.command == "lint":
        result = lint_memory_root(
            args.root,
            strict=args.strict,
            review_window_days=args.review_window_days,
            word_warning_threshold=args.word_warning_threshold,
        )
        if args.format == "json":
            print(format_lint_json(result))
        else:
            print(format_lint_text(result))
        return result.exit_code
    raise AssertionError(f"unhandled command {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
