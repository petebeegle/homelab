"""Process execution helpers for the Foundry blue/green workflow."""

from __future__ import annotations

import subprocess
from dataclasses import dataclass
from typing import Sequence

from .errors import FoundryBlueGreenError


@dataclass
class CommandResult:
    args: Sequence[str]
    stdout: str = ""
    stderr: str = ""
    returncode: int = 0


class CommandRunner:
    def run(self, args: Sequence[str], *, input_text: str | None = None) -> CommandResult:
        completed = subprocess.run(
            list(args),
            input=input_text,
            text=True,
            capture_output=True,
            check=False,
        )
        if completed.returncode != 0:
            rendered = " ".join(args)
            detail = completed.stderr.strip() or completed.stdout.strip()
            raise FoundryBlueGreenError(f"command failed: {rendered}\n{detail}")
        return CommandResult(args=args, stdout=completed.stdout, stderr=completed.stderr, returncode=0)
