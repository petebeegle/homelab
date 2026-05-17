"""Kubernetes command helpers for development verification."""

from __future__ import annotations

import shlex
import subprocess
from pathlib import Path
from types import SimpleNamespace
from typing import Sequence

from .config import AppConfig, Duration, Runner, VerificationError


def kubectl(config: AppConfig, *args: str) -> list[str]:
    return ["kubectl", "--kubeconfig", str(config.kubeconfig), *args]


def apply_activation(config: AppConfig, rendered: str, *, runner: Runner) -> None:
    run_command(
        kubectl(config, "apply", "-f", "-"),
        runner=runner,
        timeout=config.timeout,
        input_text=rendered,
    )


def run_command(
    args: Sequence[str],
    *,
    runner: Runner,
    timeout: Duration,
    cwd: Path | None = None,
    input_text: str | None = None,
    capture_output: bool = False,
    success_codes: tuple[int, ...] = (0,),
) -> subprocess.CompletedProcess[str] | SimpleNamespace:
    if not getattr(runner, "quiet", False):
        print("+ " + shlex.join(str(arg) for arg in args))
    try:
        result = runner(
            [str(arg) for arg in args],
            cwd=str(cwd) if cwd is not None else None,
            input=input_text,
            text=True,
            capture_output=capture_output,
            timeout=timeout.seconds,
        )
    except subprocess.TimeoutExpired as exc:
        raise VerificationError(f"command timed out after {timeout.raw}: {shlex.join(str(arg) for arg in args)}") from exc

    returncode = int(getattr(result, "returncode", 0))
    if returncode not in success_codes:
        raise VerificationError(
            f"command failed with exit code {returncode}: {shlex.join(str(arg) for arg in args)}"
        )
    return result
