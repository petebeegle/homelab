#!/usr/bin/env python3
"""Render a deterministic Codex context pack for a task."""

from __future__ import annotations

import argparse
import sys
from datetime import date
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from context_pack.frontmatter import is_inactive as _is_inactive
from context_pack.frontmatter import split_frontmatter
from context_pack.manifest import parse_manifest
from context_pack.models import Source
from context_pack.rendering import commit_sha as _commit_sha
from context_pack.rendering import excerpt, metadata_line
from context_pack.rendering import render_pack as _render_pack
from context_pack.selection import ALWAYS_INCLUDE, score_source, tokenize
from context_pack.selection import excluded as _excluded
from context_pack.selection import select_sources as _select_sources
from homelab_tools.yamlish import strip_quotes


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MANIFEST = ".codex/retrieval.yaml"
DEFAULT_INDEX = "binding-agent-context"
DEFAULT_LIMIT = 8


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="context-pack")
    parser.add_argument("--task", required=True, help="Task description used for deterministic matching")
    parser.add_argument("--manifest", default=DEFAULT_MANIFEST, help="Retrieval manifest path")
    parser.add_argument("--index", default=DEFAULT_INDEX, help="Retrieval index name")
    parser.add_argument("--limit", type=int, default=DEFAULT_LIMIT, help="Maximum matched sources")
    args = parser.parse_args(argv)

    manifest = parse_manifest(ROOT / args.manifest, args.index)
    sources = select_sources(args.task, manifest, limit=args.limit)
    print(render_pack(args.task, sources))
    return 0


def select_sources(task: str, manifest: dict[str, list[str]], *, limit: int) -> list[Source]:
    return _select_sources(
        task,
        manifest,
        limit=limit,
        root=ROOT,
        always_include=ALWAYS_INCLUDE,
    )


def render_pack(task: str, sources: list[Source]) -> str:
    return _render_pack(task, sources, commit_func=commit_sha)


def is_inactive(metadata: dict[str, object], today: date) -> bool:
    return _is_inactive(metadata, today)


def excluded(path: Path, exclude_patterns: list[str]) -> bool:
    return _excluded(path, exclude_patterns, root=ROOT)


def commit_sha() -> str:
    return _commit_sha(ROOT)


if __name__ == "__main__":
    raise SystemExit(main())
