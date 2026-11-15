#!/usr/bin/env python3
"""Single verification contract for local agents and CI.

This is intentionally a narrow, dependency-free foundation, not a claim
that full integration or browser E2E verification has run.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

PROFILES = {
    "harness": (
        (sys.executable, "-m", "unittest", "discover", "-s", "tools/verification/tests"),
        (sys.executable, "-m", "unittest", "discover", "-s", "tools/development/runner/tests"),
        ("node", "--test", "tests/browser/tests/url-guard.test.cjs"),
    ),
}


def run_commands(commands, *, cwd=ROOT, runner=subprocess.run):
    for command in commands:
        try:
            result = runner(command, cwd=cwd, check=False)
        except OSError as exc:
            print(f"BLOCKED: could not run {command[0]}: {exc}", file=sys.stderr)
            return 127
        if result.returncode != 0:
            print(f"FAILED: {command[0]} returned {result.returncode}", file=sys.stderr)
            return result.returncode
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", choices=sorted(PROFILES), required=True)
    args = parser.parse_args(argv)
    return run_commands(PROFILES[args.profile])


if __name__ == "__main__":
    raise SystemExit(main())
