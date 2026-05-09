"""Placeholder for a future Codex MCP bridge.

The local scaffold deliberately keeps memory writes file-based for now. This
module exists so the eventual MCP adapter has a stable import target without
coupling the current CLI to a server runtime.
"""

from __future__ import annotations


def describe_capabilities() -> dict[str, object]:
    return {
        "status": "placeholder",
        "capabilities": [
            "compact_transcript",
            "extract_candidates",
            "review_policy",
            "consolidate_reviewed",
        ],
    }
