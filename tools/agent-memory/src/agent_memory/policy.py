"""Review policy for memory candidates."""

from __future__ import annotations

import re

from agent_memory.models import MemoryCandidate

SECRET_PATTERNS = (
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----", re.I),
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    re.compile(r"\b(?:api[_-]?key|secret|token|password)\b\s*[:=]\s*['\"]?[^'\"\s]{8,}", re.I),
    re.compile(r"\bgh[pousr]_[A-Za-z0-9_]{20,}\b"),
)


def secret_rejection_reason(text: str) -> str | None:
    for pattern in SECRET_PATTERNS:
        if pattern.search(text):
            return "candidate appears to contain a secret or credential"
    return None


def apply_review_policy(candidate: MemoryCandidate) -> MemoryCandidate:
    reason = secret_rejection_reason(candidate.text)
    if reason is None:
        return candidate
    return MemoryCandidate(
        candidate_id=candidate.candidate_id,
        kind=candidate.kind,
        text=candidate.text,
        source=candidate.source,
        created_at=candidate.created_at,
        reviewed=False,
        rejected=True,
        rejection_reason=reason,
    )


def assert_promotable(candidate: MemoryCandidate) -> None:
    if candidate.rejected:
        raise ValueError(f"candidate {candidate.candidate_id} is rejected: {candidate.rejection_reason}")
    if not candidate.reviewed:
        raise ValueError(f"candidate {candidate.candidate_id} has not been reviewed")
