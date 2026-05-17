"""Path helpers for direct repository scripts."""

from __future__ import annotations

import sys
from pathlib import Path


def repo_root_from_file(file: str | Path, *, marker: str = ".git") -> Path:
    """Return the nearest parent containing the requested repository marker."""
    path = Path(file).resolve()
    for parent in (path.parent, *path.parents):
        if (parent / marker).exists():
            return parent
    raise ValueError(f"Unable to find repository root from {path}")


def add_tools_lib_to_syspath(root: Path) -> Path:
    """Add the repo-local tools/lib path to sys.path and return it."""
    tools_lib = root / "tools" / "lib"
    value = str(tools_lib)
    if value not in sys.path:
        sys.path.insert(0, value)
    return tools_lib
