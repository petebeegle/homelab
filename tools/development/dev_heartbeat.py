#!/usr/bin/env python3
"""Fail when nothing has succeeded on the in-cluster dev runner recently.

Reads GitHub Actions job objects on stdin, one JSON object per line, as printed by
`gh api repos/<repo>/actions/runs/<id>/jobs --jq '.jobs[]'` for recent runs of the
workflows that use the dev runner (dev-cleanup, and dev-smoke's smoke job). A job
counts when it carries the runner label, was picked up by a runner, and succeeded:
each of those can only happen when the runner pod can start and reach the dev
cluster. A stale or missing success means the runner or the dev cluster is down.
Exit 0 when healthy, 1 otherwise.
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


def _read_jobs(stdin) -> list[dict]:
    jobs = [json.loads(line) for line in stdin.read().splitlines() if line.strip()]
    for job in jobs:
        if not isinstance(job, dict):
            raise TypeError(f"expected a job object, got {job!r}")
    return jobs


def main(argv=None, *, stdin=None, stdout=None, stderr=None, now: datetime | None = None) -> int:
    stdin = stdin or sys.stdin
    stdout = stdout or sys.stdout
    stderr = stderr or sys.stderr
    now = now or datetime.now(timezone.utc)

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runner-label", required=True, help="runs-on label of the dev runner, e.g. homelab-dev")
    parser.add_argument("--max-age-seconds", required=True, type=int)
    args = parser.parse_args(argv)
    label = args.runner_label

    try:
        successes = [
            (_parse(job["completed_at"]), f"{job.get('workflow_name', '?')} / {job.get('name', '?')}")
            for job in _read_jobs(stdin)
            if job.get("conclusion") == "success" and label in (job.get("labels") or []) and job.get("runner_name")
        ]
    except (ValueError, KeyError, TypeError, AttributeError) as exc:
        print(f"could not read the job list: {exc!r}", file=stderr)
        return 1

    if not successes:
        print(f"no successful job on the {label} runner found: the dev runner or cluster may be down", file=stderr)
        return 1

    newest, which = max(successes)
    age = int((now - newest).total_seconds())
    if age > args.max_age_seconds:
        print(
            f"nothing has succeeded on the {label} runner for {_format_age(age)} "
            f"(limit {_format_age(args.max_age_seconds)}; last was {which}): the dev runner or cluster may be down",
            file=stderr,
        )
        return 1
    print(f"{label} runner last succeeded {_format_age(age)} ago ({which})", file=stdout)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
