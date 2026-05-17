"""Data models for context-pack rendering."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class Source:
    path: Path
    metadata: dict[str, object]
    body: str
    score: int
    root: Path = field(default_factory=lambda: Path(__file__).resolve().parents[3])

    @property
    def relative_path(self) -> str:
        return self.path.relative_to(self.root).as_posix()
