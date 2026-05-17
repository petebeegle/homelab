"""Source discovery and scoring for context packs."""

from __future__ import annotations

import fnmatch
import re
from datetime import datetime, timezone
from pathlib import Path

from .frontmatter import is_inactive, split_frontmatter
from .models import Source


ALWAYS_INCLUDE = ("AGENTS.md",)


def select_sources(
    task: str,
    manifest: dict[str, list[str]],
    *,
    limit: int,
    root: Path,
    always_include: tuple[str, ...] = ALWAYS_INCLUDE,
) -> list[Source]:
    task_terms = tokenize(task)
    today = datetime.now(timezone.utc).date()
    candidates: dict[str, Path] = {}

    for pattern in manifest["include"]:
        for path in root.glob(pattern):
            if path.is_file() and not excluded(path, manifest["exclude"], root=root):
                candidates[path.relative_to(root).as_posix()] = path

    sources: list[Source] = []
    for relative_path, path in sorted(candidates.items()):
        metadata, body = split_frontmatter(path.read_text(encoding="utf-8"))
        if is_inactive(metadata, today):
            continue
        score = score_source(relative_path, body, task_terms)
        if relative_path in always_include:
            score += 100
        if score > 0:
            sources.append(Source(path=path, metadata=metadata, body=body, score=score, root=root))

    return sorted(sources, key=lambda source: (-source.score, source.relative_path))[:limit]


def score_source(path: str, body: str, task_terms: set[str]) -> int:
    haystack = tokenize(path) | tokenize(body)
    return len(task_terms & haystack)


def excluded(path: Path, exclude_patterns: list[str], *, root: Path) -> bool:
    relative = path.relative_to(root).as_posix()
    return any(fnmatch.fnmatch(relative, pattern) for pattern in exclude_patterns)


def tokenize(value: str) -> set[str]:
    return {token for token in re.findall(r"[a-z0-9]+", value.lower()) if len(token) > 2}
