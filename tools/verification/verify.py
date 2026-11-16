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

# Test files the harness must NOT run, each with the reason. Everything else that looks
# like a test is discovered and run, so a new test file is gated without editing this file.
EXCLUDED = {
    "tools/development/tests/test_jellyfin_manifests.py": (
        "needs the jellyfin Helm chart repository; the Kubernetes job in ci.yml adds it and runs this test"
    ),
    "tools/vpn/test_defaults.mjs": (
        "needs the libsql client from the wg-easy image; not runnable on a plain CI runner (see issue #477)"
    ),
}

NODE_TEST_PATTERNS = ("*.test.js", "*.test.cjs", "*.test.mjs", "test_*.mjs")
SKIPPED_DIRECTORIES = {"node_modules", "__pycache__", ".git", ".codex", ".superpowers"}


def _walk(root: Path, pattern: str):
    for path in sorted(root.rglob(pattern)):
        if path.is_file() and not SKIPPED_DIRECTORIES.intersection(path.relative_to(root).parts):
            yield path


def python_test_files(root: Path = ROOT) -> list[str]:
    tools = root / "tools"
    return [path.relative_to(root).as_posix() for path in _walk(tools, "test_*.py")] if tools.is_dir() else []


def node_test_files(root: Path = ROOT) -> list[str]:
    found = {path.relative_to(root).as_posix() for pattern in NODE_TEST_PATTERNS for path in _walk(root, pattern)}
    return sorted(found)


def harness_commands(root: Path = ROOT) -> tuple[tuple[str, ...], ...]:
    commands: list[tuple[str, ...]] = []
    for relative in python_test_files(root):
        if relative in EXCLUDED:
            continue
        directory, _, name = relative.rpartition("/")
        commands.append((sys.executable, "-m", "unittest", "discover", "-s", directory, "-p", name))
    for relative in node_test_files(root):
        if relative not in EXCLUDED:
            commands.append(("node", "--test", relative))
    return tuple(commands)


PROFILES = {
    "harness": harness_commands(),
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
