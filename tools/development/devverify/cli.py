"""Command-line entry point for development branch verification."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Sequence

from .config import DEFAULT_KUBECONFIG, DEFAULT_TIMEOUT, VerificationError, config_from_args, parse_duration, validate_app, validate_branch, validate_slug
from .profiles import supported_apps
from .workflow import run_acceptance


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Verify an app branch environment on the homelab development cluster."
    )
    parser.add_argument("--app", required=True, type=validate_app, choices=sorted(supported_apps()))
    parser.add_argument("--branch", required=True, type=validate_branch)
    parser.add_argument("--slug", required=True, type=validate_slug)
    parser.add_argument("--push", action="store_true", help="Push current HEAD to origin as --branch before activation.")
    parser.add_argument("--terraform-apply", action="store_true", help="Run terraform apply after a successful plan.")
    parser.add_argument(
        "--include-cluster-base",
        action="store_true",
        help="Temporarily reconcile the development base from --branch before branch app verification.",
    )
    parser.add_argument("--kubeconfig", type=Path, default=DEFAULT_KUBECONFIG)
    parser.add_argument("--timeout", type=parse_duration, default=parse_duration(DEFAULT_TIMEOUT))
    parser.add_argument("--keep", action="store_true", help="Keep branch Flux resources for debugging.")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    config = config_from_args(args)
    try:
        run_acceptance(config)
    except VerificationError as exc:
        print(f"verification failed: {exc}", file=sys.stderr)
        return 1
    return 0
