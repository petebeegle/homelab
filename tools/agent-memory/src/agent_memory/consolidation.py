"""Consolidate reviewed memory candidates into durable memory."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from agent_memory.models import MemoryCandidate, utc_now
from agent_memory.policy import assert_promotable
from agent_memory.storage import append_jsonl, ensure_memory_tree, read_jsonl


@dataclass(frozen=True)
class ConsolidationPlan:
    promoted: tuple[MemoryCandidate, ...]
    dry_run: bool

    def to_record(self) -> dict[str, object]:
        return {
            "dry_run": self.dry_run,
            "promoted_count": len(self.promoted),
            "candidate_ids": [candidate.candidate_id for candidate in self.promoted],
        }


def consolidate_candidates(
    candidates: list[MemoryCandidate],
    root: str | Path | None = None,
    *,
    dry_run: bool = True,
) -> ConsolidationPlan:
    for candidate in candidates:
        assert_promotable(candidate)

    plan = ConsolidationPlan(promoted=tuple(candidates), dry_run=dry_run)
    if dry_run:
        return plan

    base = ensure_memory_tree(root)
    records = []
    for candidate in candidates:
        record = candidate.to_record()
        record["consolidated_at"] = utc_now()
        records.append(record)
    append_jsonl(base / "approved" / "memory.jsonl", records)
    return plan


def load_reviewed_candidates(root: str | Path | None = None) -> list[MemoryCandidate]:
    base = ensure_memory_tree(root)
    records = read_jsonl(base / "candidates" / "reviewed.jsonl")
    return [MemoryCandidate.from_record(record) for record in records]
