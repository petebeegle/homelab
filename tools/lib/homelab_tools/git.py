"""Git discovery helpers for local scripts."""

from __future__ import annotations

from pathlib import Path

from homelab_tools.process import output


def discover_git_root(cwd: Path) -> Path | None:
    result = output(["git", "rev-parse", "--show-toplevel"], cwd=cwd, as_path=True)
    return result if isinstance(result, Path) else None


def discover_git_branch(cwd: Path) -> str | None:
    result = output(["git", "branch", "--show-current"], cwd=cwd)
    return result if isinstance(result, str) else None


def discover_git_head(cwd: Path) -> str | None:
    result = output(["git", "rev-parse", "HEAD"], cwd=cwd)
    return result if isinstance(result, str) else None
