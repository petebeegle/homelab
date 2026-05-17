"""Process execution helpers for the Foundry blue/green workflow."""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

from .errors import FoundryBlueGreenError

TOOLS_LIB = Path(__file__).resolve().parents[1] / "lib"
if str(TOOLS_LIB) not in sys.path:
    sys.path.insert(0, str(TOOLS_LIB))

from homelab_tools.process import run as run_process


@dataclass
class CommandResult:
    args: Sequence[str]
    stdout: str = ""
    stderr: str = ""
    returncode: int = 0


class CommandRunner:
    def run(self, args: Sequence[str], *, input_text: str | None = None) -> CommandResult:
        completed = run_process(args, input_text=input_text)
        if not completed.ok():
            rendered = " ".join(args)
            detail = completed.stderr.strip() or completed.stdout.strip()
            raise FoundryBlueGreenError(f"command failed: {rendered}\n{detail}")
        return CommandResult(
            args=args,
            stdout=completed.stdout,
            stderr=completed.stderr,
            returncode=completed.returncode,
        )
