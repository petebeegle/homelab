"""Markdown rendering for context packs."""

from __future__ import annotations

import subprocess
from collections.abc import Callable
from pathlib import Path

from .models import Source


def render_pack(
    task: str,
    sources: list[Source],
    *,
    commit_func: Callable[[], str] | None = None,
) -> str:
    if commit_func is None:
        def default_commit_sha() -> str:
            return commit_sha(Path(__file__).resolve().parents[3])

        commit_func = default_commit_sha

    lines = [
        "# Context Pack",
        "",
        f"Task: {task}",
        f"Commit: {commit_func()}",
        "",
        "## Sources",
    ]
    for source in sources:
        lines.extend(
            [
                "",
                f"### {source.relative_path}",
                "",
                metadata_line(source),
                "",
                excerpt(source.body),
            ]
        )
    return "\n".join(lines).rstrip() + "\n"


def metadata_line(source: Source) -> str:
    metadata = source.metadata
    fields = {
        "kind": metadata.get("kind", "document"),
        "status": metadata.get("status", "unknown"),
        "authority": metadata.get("authority", "unspecified"),
        "scope": ",".join(metadata.get("scope", [])) if isinstance(metadata.get("scope"), list) else "",
    }
    return "Metadata: " + "; ".join(f"{key}={value}" for key, value in fields.items() if value)


def excerpt(body: str, *, max_lines: int = 16) -> str:
    selected = [line.rstrip() for line in body.splitlines() if line.strip()]
    return "\n".join(selected[:max_lines])


def commit_sha(root: Path) -> str:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=root,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True,
        check=False,
    )
    return result.stdout.strip() or "unknown"
