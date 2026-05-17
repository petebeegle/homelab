"""Foundry blue/green workflow exceptions."""

from __future__ import annotations


class FoundryBlueGreenError(RuntimeError):
    """Raised when a workflow precondition fails."""
