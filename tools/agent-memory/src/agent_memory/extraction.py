"""Candidate extraction from compacted conversation text."""

from __future__ import annotations

import re

from agent_memory.models import MemoryCandidate
from agent_memory.policy import apply_review_policy

MARKER_PATTERN = re.compile(r"\b(?:remember|preference|decision|fact|todo|follow-up)\b\s*[:\-]\s*(.+)", re.I)


def extract_candidates(text: str, source: str = "transcript") -> list[MemoryCandidate]:
    """Extract conservative memory candidates from marked lines.

    This scaffold intentionally avoids broad inference. A line must include an
    explicit memory-ish marker before it can become a candidate.
    """

    candidates: list[MemoryCandidate] = []
    for line in text.splitlines():
        stripped = line.strip(" -\t")
        if not stripped:
            continue
        match = MARKER_PATTERN.search(stripped)
        if not match:
            continue
        candidate_text = match.group(1).strip()
        if not candidate_text:
            continue
        kind = stripped.split(":", 1)[0].lower() if ":" in stripped else "note"
        candidates.append(apply_review_policy(MemoryCandidate(text=candidate_text, source=source, kind=kind)))
    return candidates
