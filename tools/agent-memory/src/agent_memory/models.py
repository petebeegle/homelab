"""Shared data models for the local memory scaffold."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


@dataclass(frozen=True)
class MemoryCandidate:
    """A fact-like item extracted from conversation context."""

    text: str
    source: str
    kind: str = "note"
    candidate_id: str = field(default_factory=lambda: str(uuid4()))
    created_at: str = field(default_factory=utc_now)
    reviewed: bool = False
    rejected: bool = False
    rejection_reason: str | None = None

    def to_record(self) -> dict[str, Any]:
        return {
            "candidate_id": self.candidate_id,
            "kind": self.kind,
            "text": self.text,
            "source": self.source,
            "created_at": self.created_at,
            "reviewed": self.reviewed,
            "rejected": self.rejected,
            "rejection_reason": self.rejection_reason,
        }

    @classmethod
    def from_record(cls, record: dict[str, Any]) -> "MemoryCandidate":
        return cls(
            candidate_id=record["candidate_id"],
            kind=record.get("kind", "note"),
            text=record["text"],
            source=record.get("source", "unknown"),
            created_at=record.get("created_at", utc_now()),
            reviewed=bool(record.get("reviewed", False)),
            rejected=bool(record.get("rejected", False)),
            rejection_reason=record.get("rejection_reason"),
        )


@dataclass(frozen=True)
class CompactionCheckpoint:
    """A checkpoint that records what context was compacted."""

    checkpoint_id: str
    summary: str
    source: str
    created_at: str = field(default_factory=utc_now)
    candidate_ids: tuple[str, ...] = ()

    def to_record(self) -> dict[str, Any]:
        return {
            "checkpoint_id": self.checkpoint_id,
            "summary": self.summary,
            "source": self.source,
            "created_at": self.created_at,
            "candidate_ids": list(self.candidate_ids),
        }
