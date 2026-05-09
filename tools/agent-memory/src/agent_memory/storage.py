"""Filesystem helpers for local memory JSONL storage."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Iterable

DEFAULT_MEMORY_ROOT = Path(".codex/memory")
MEMORY_SUBDIRS = (
    "checkpoints",
    "candidates",
    "approved",
    "rejected",
    "reports",
)


def memory_root(root: str | Path | None = None) -> Path:
    configured = root or os.environ.get("CODEX_MEMORY_ROOT") or DEFAULT_MEMORY_ROOT
    return Path(configured)


def ensure_memory_tree(root: str | Path | None = None) -> Path:
    base = memory_root(root)
    for subdir in MEMORY_SUBDIRS:
        directory = base / subdir
        directory.mkdir(parents=True, exist_ok=True)
        gitkeep = directory / ".gitkeep"
        if not gitkeep.exists():
            gitkeep.write_text("", encoding="utf-8")
    return base


def append_jsonl(path: Path, records: Iterable[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, sort_keys=True) + "\n")


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def write_json(path: Path, record: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8")
