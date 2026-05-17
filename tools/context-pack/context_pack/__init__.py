"""Importable context-pack renderer package."""

from __future__ import annotations

import sys
from pathlib import Path


TOOLS_LIB = Path(__file__).resolve().parents[2] / "lib"
if str(TOOLS_LIB) not in sys.path:
    sys.path.insert(0, str(TOOLS_LIB))

from .frontmatter import is_inactive, split_frontmatter
from .manifest import parse_manifest
from .models import Source
from .rendering import commit_sha, excerpt, metadata_line, render_pack
from .selection import excluded, score_source, select_sources, tokenize

__all__ = [
    "Source",
    "commit_sha",
    "excluded",
    "excerpt",
    "is_inactive",
    "metadata_line",
    "parse_manifest",
    "render_pack",
    "score_source",
    "select_sources",
    "split_frontmatter",
    "tokenize",
]
