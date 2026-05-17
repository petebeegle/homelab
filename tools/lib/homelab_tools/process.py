"""Small subprocess helpers for repository tooling."""

from __future__ import annotations

import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, Sequence


@dataclass(frozen=True)
class CommandResult:
    """Captured command result that never requires subprocess exceptions."""

    args: tuple[str, ...]
    returncode: int
    stdout: str
    stderr: str
    _success_codes: tuple[int, ...] = field(default=(0,), repr=False, compare=False)

    @property
    def success(self) -> bool:
        return self.ok()

    def ok(self, success_codes: Iterable[int] | None = None) -> bool:
        codes = self._success_codes if success_codes is None else tuple(success_codes)
        return self.returncode in set(codes)


def run(
    command: Sequence[str],
    *,
    cwd: Path | None = None,
    input_text: str | None = None,
    timeout: float | None = None,
    success_codes: Iterable[int] = (0,),
) -> CommandResult:
    """Run a command safely, capturing stdout and stderr without raising."""
    args = tuple(str(part) for part in command)
    success_codes = tuple(success_codes)
    try:
        result = subprocess.run(
            args,
            cwd=cwd,
            input=input_text,
            timeout=timeout,
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
    except subprocess.TimeoutExpired as exc:
        stdout = _to_text(exc.stdout)
        stderr = _to_text(exc.stderr)
        if stderr:
            stderr = f"{stderr}\ncommand timed out after {timeout} seconds"
        else:
            stderr = f"command timed out after {timeout} seconds"
        return CommandResult(
            args=args,
            returncode=124,
            stdout=stdout,
            stderr=stderr,
            _success_codes=success_codes,
        )
    except OSError as exc:
        return CommandResult(
            args=args,
            returncode=127,
            stdout="",
            stderr=str(exc),
            _success_codes=success_codes,
        )

    return CommandResult(
        args=args,
        returncode=result.returncode,
        stdout=result.stdout,
        stderr=result.stderr,
        _success_codes=success_codes,
    )


def output(
    command: Sequence[str],
    *,
    cwd: Path,
    as_path: bool = False,
) -> str | Path | None:
    """Run a command and return stripped stdout, or None on command failure."""
    try:
        result = subprocess.run(
            command,
            cwd=cwd,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
        )
    except (FileNotFoundError, subprocess.CalledProcessError):
        return None

    value = result.stdout.strip()
    if not value:
        return None
    return Path(value) if as_path else value


def _to_text(value: str | bytes | None) -> str:
    if value is None:
        return ""
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    return value
