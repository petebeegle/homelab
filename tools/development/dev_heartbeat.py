#!/usr/bin/env python3
"""Fail when the dev-cleanup workflow has not succeeded recently.

Reads the JSON from `gh api repos/<repo>/actions/workflows/dev-cleanup.yml/runs?status=success`
on stdin. dev-cleanup runs on the dev runner every 30 minutes, so a stale or missing success
means the runner or the dev cluster is down. Exit 0 when healthy, 1 otherwise.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone


def _parse(timestamp: str) -> datetime:
    return datetime.fromisoformat(timestamp.replace("Z", "+00:00"))


def _format_age(seconds: int) -> str:
    hours, rest = divmod(seconds, 3600)
    return f"{hours}h{rest // 60:02d}m"


def main(argv=None, *, stdin=None, stdout=None, stderr=None, now: datetime | None = None) -> int:
    stdin = stdin or sys.stdin
    stdout = stdout or sys.stdout
    stderr = stderr or sys.stderr
    now = now or datetime.now(timezone.utc)

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--max-age-seconds", required=True, type=int)
    args = parser.parse_args(argv)

    try:
        runs = json.load(stdin)["workflow_runs"]
        stamps = [_parse(run["updated_at"]) for run in runs if run.get("conclusion") == "success"]
    except (ValueError, KeyError, TypeError) as exc:
        print(f"could not read the dev-cleanup run list: {exc!r}", file=stderr)
        return 1

    if not stamps:
        print("no successful dev-cleanup run found: the dev runner or cluster may be down", file=stderr)
        return 1

    age = int((now - max(stamps)).total_seconds())
    if age > args.max_age_seconds:
        print(
            f"dev-cleanup last succeeded {_format_age(age)} ago (limit {_format_age(args.max_age_seconds)}): "
            "the dev runner or cluster may be down",
            file=stderr,
        )
        return 1
    print(f"dev-cleanup last succeeded {_format_age(age)} ago", file=stdout)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
