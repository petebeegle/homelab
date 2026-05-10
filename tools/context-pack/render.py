#!/usr/bin/env python3
"""Render a deterministic Codex context pack for a task."""

from __future__ import annotations

import argparse
import fnmatch
import re
import subprocess
from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MANIFEST = ".codex/retrieval.yaml"
DEFAULT_INDEX = "binding-agent-context"
DEFAULT_LIMIT = 8
ALWAYS_INCLUDE = ("AGENTS.md",)


@dataclass(frozen=True)
class Source:
    path: Path
    metadata: dict[str, object]
    body: str
    score: int

    @property
    def relative_path(self) -> str:
        return self.path.relative_to(ROOT).as_posix()


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


def parse_manifest(path: Path, index_name: str) -> dict[str, list[str]]:
    indexes: list[dict[str, object]] = []
    current: dict[str, object] | None = None
    current_list: str | None = None

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.split("#", 1)[0].rstrip()
        if not line.strip() or line.strip() in {"---", "indexes:"}:
            continue
        if line.startswith("  - name: "):
            current = {"name": strip_quotes(line.split(":", 1)[1].strip())}
            indexes.append(current)
            current_list = None
            continue
        if current is None:
            continue
        if line.startswith("    ") and line.endswith(":"):
            current_list = line.strip()[:-1]
            current[current_list] = []
            continue
        if line.startswith("      - ") and current_list:
            values = current[current_list]
            if isinstance(values, list):
                values.append(strip_quotes(line.strip()[2:].strip()))

    for index in indexes:
        if index.get("name") == index_name:
            return {
                "include": list(index.get("include", [])),
                "exclude": list(index.get("exclude", [])),
                "required_metadata": list(index.get("required_metadata", [])),
            }

    raise SystemExit(f"retrieval index not found: {index_name}")


def select_sources(task: str, manifest: dict[str, list[str]], *, limit: int) -> list[Source]:
    task_terms = tokenize(task)
    today = datetime.now(timezone.utc).date()
    candidates: dict[str, Path] = {}

    for pattern in manifest["include"]:
        for path in ROOT.glob(pattern):
            if path.is_file() and not excluded(path, manifest["exclude"]):
                candidates[path.relative_to(ROOT).as_posix()] = path

    sources: list[Source] = []
    for relative_path, path in sorted(candidates.items()):
        metadata, body = split_frontmatter(path.read_text(encoding="utf-8"))
        if is_inactive(metadata, today):
            continue
        score = score_source(relative_path, body, task_terms)
        if relative_path in ALWAYS_INCLUDE:
            score += 100
        if score > 0:
            sources.append(Source(path=path, metadata=metadata, body=body, score=score))

    return sorted(sources, key=lambda source: (-source.score, source.relative_path))[:limit]


def render_pack(task: str, sources: list[Source]) -> str:
    lines = [
        "# Context Pack",
        "",
        f"Task: {task}",
        f"Commit: {commit_sha()}",
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


def split_frontmatter(text: str) -> tuple[dict[str, object], str]:
    lines = text.splitlines()
    if not lines or lines[0] != "---":
        return {}, text
    try:
        end = lines[1:].index("---") + 1
    except ValueError:
        return {}, text

    metadata: dict[str, object] = {}
    current_list: str | None = None
    for line in lines[1:end]:
        if not line.strip():
            continue
        if line.startswith("  - ") and current_list:
            values = metadata[current_list]
            if isinstance(values, list):
                values.append(strip_quotes(line[4:].strip()))
            continue
        current_list = None
        if ":" not in line:
            continue
        key, raw_value = line.split(":", 1)
        key = key.strip()
        value = raw_value.strip()
        if value == "[]":
            metadata[key] = []
        elif value == "":
            metadata[key] = []
            current_list = key
        else:
            metadata[key] = strip_quotes(value)
    return metadata, "\n".join(lines[end + 1 :]).strip()


def is_inactive(metadata: dict[str, object], today: date) -> bool:
    superseded_by = metadata.get("superseded_by")
    if isinstance(superseded_by, list) and superseded_by:
        return True

    review_after = metadata.get("review_after")
    if isinstance(review_after, str):
        try:
            return today > date.fromisoformat(review_after)
        except ValueError:
            return False
    return False


def score_source(path: str, body: str, task_terms: set[str]) -> int:
    haystack = tokenize(path) | tokenize(body)
    return len(task_terms & haystack)


def excluded(path: Path, exclude_patterns: list[str]) -> bool:
    relative = path.relative_to(ROOT).as_posix()
    return any(fnmatch.fnmatch(relative, pattern) for pattern in exclude_patterns)


def excerpt(body: str, *, max_lines: int = 16) -> str:
    selected = [line.rstrip() for line in body.splitlines() if line.strip()]
    return "\n".join(selected[:max_lines])


def tokenize(value: str) -> set[str]:
    return {token for token in re.findall(r"[a-z0-9]+", value.lower()) if len(token) > 2}


def strip_quotes(value: str) -> str:
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        return value[1:-1]
    return value


def commit_sha() -> str:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True,
        check=False,
    )
    return result.stdout.strip() or "unknown"


if __name__ == "__main__":
    raise SystemExit(main())
