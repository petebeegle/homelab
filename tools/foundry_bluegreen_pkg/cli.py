"""CLI parser and dispatch for the Foundry blue/green workflow."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Iterable

from .config import DESCRIPTION, DEV_KUBECONFIG, EVIDENCE_PATH, ROOT
from .errors import FoundryBlueGreenError
from .process import CommandRunner
from .workflow import (
    command_dev_rehearse,
    command_prepare,
    command_promote,
    command_retire,
    command_rollback,
    command_status,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    parser.add_argument("--root", type=Path, default=ROOT, help="repository root")
    parser.add_argument("--evidence", type=Path, default=EVIDENCE_PATH, help="dev rehearsal evidence path")
    subparsers = parser.add_subparsers(dest="command", required=True)

    def add_common_options(command_parser: argparse.ArgumentParser) -> None:
        command_parser.add_argument("--root", type=Path, default=argparse.SUPPRESS, help="repository root")
        command_parser.add_argument(
            "--evidence",
            type=Path,
            default=argparse.SUPPRESS,
            help="dev rehearsal evidence path",
        )

    status = subparsers.add_parser("status", help="show active color and dev gate status")
    add_common_options(status)

    dev = subparsers.add_parser("dev-rehearse", help="exercise the safe development fixture")
    add_common_options(dev)
    dev.add_argument("--kubeconfig", default=str(DEV_KUBECONFIG), help="development kubeconfig")

    prepare = subparsers.add_parser("prepare", help="prepare green Foundry desired state")
    add_common_options(prepare)
    prepare.add_argument("--image", required=True, help="Foundry image, for example felddy/foundryvtt:14.361")

    promote = subparsers.add_parser("promote", help="move stable production service to green desired state")
    add_common_options(promote)
    rollback = subparsers.add_parser("rollback", help="move stable production service back to blue desired state")
    add_common_options(rollback)
    retire = subparsers.add_parser("retire", help="remove inactive desired state after the outcome is accepted")
    add_common_options(retire)
    return parser


def dispatch(args: argparse.Namespace, runner: CommandRunner | None = None) -> int:
    runner = runner or CommandRunner()
    if args.command == "status":
        return command_status(args)
    if args.command == "dev-rehearse":
        return command_dev_rehearse(args, runner)
    if args.command == "prepare":
        return command_prepare(args)
    if args.command == "promote":
        return command_promote(args)
    if args.command == "rollback":
        return command_rollback(args)
    if args.command == "retire":
        return command_retire(args)
    raise FoundryBlueGreenError(f"unknown command: {args.command}")


def main(argv: Iterable[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(list(argv) if argv is not None else None)
    args.root = args.root.resolve()
    try:
        return dispatch(args)
    except FoundryBlueGreenError as exc:
        print(str(exc), file=sys.stderr)
        return 2
