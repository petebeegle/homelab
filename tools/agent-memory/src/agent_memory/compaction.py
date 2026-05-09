"""Compaction checkpointing for local memory."""

from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from agent_memory.extraction import extract_candidates
from agent_memory.models import CompactionCheckpoint
from agent_memory.storage import append_jsonl, ensure_memory_tree, write_json


def summarize_text(text: str, max_chars: int = 1200) -> str:
    normalized = " ".join(text.split())
    if len(normalized) <= max_chars:
        return normalized
    return normalized[: max_chars - 3].rstrip() + "..."


def compact_transcript(text: str, root: str | Path | None = None, source: str = "transcript") -> CompactionCheckpoint:
    base = ensure_memory_tree(root)
    candidates = extract_candidates(text, source=source)
    checkpoint = CompactionCheckpoint(
        checkpoint_id=str(uuid4()),
        summary=summarize_text(text),
        source=source,
        candidate_ids=tuple(candidate.candidate_id for candidate in candidates),
    )

    write_json(base / "checkpoints" / f"{checkpoint.checkpoint_id}.json", checkpoint.to_record())
    append_jsonl(base / "candidates" / "pending.jsonl", (candidate.to_record() for candidate in candidates))
    return checkpoint
