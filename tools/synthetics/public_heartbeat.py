#!/usr/bin/env python3
"""Request every internet-public host from outside the homelab and fail if one does not answer.

Run by .github/workflows/public-heartbeat.yml on a GitHub-hosted runner, so it covers what the
in-cluster synthetic smoke job cannot: public DNS, Cloudflare, the tunnel and gateway/public,
and it still runs when production (and its alerting) is down. Targets: public-targets.json.
"""
from __future__ import annotations

import json
import re
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

TARGETS = Path(__file__).resolve().parent / "public-targets.json"
USER_AGENT = "homelab-public-heartbeat"

Fetch = Callable[[str], "tuple[int, str]"]


@dataclass(frozen=True)
class Target:
    host: str
    path: str
    status: int
    body_regex: str

    @property
    def url(self) -> str:
        return f"https://{self.host}{self.path}"


def load_targets(path: Path = TARGETS) -> list[Target]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    return [Target(host=t["host"], path=t["path"], status=t["status"], body_regex=t["bodyRegex"]) for t in raw]


def fetch(url: str) -> tuple[int, str]:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            return response.status, response.read(65536).decode("utf-8", "replace")
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read(65536).decode("utf-8", "replace")


def _problem(target: Target, fetch: Fetch) -> str | None:
    try:
        status, body = fetch(target.url)
    except OSError as exc:
        return f"{target.url}: no answer ({exc})"
    if status != target.status:
        return f"{target.url}: HTTP {status}, expected {target.status}"
    if not re.search(target.body_regex, body):
        return f"{target.url}: HTTP {status} without a body matching {target.body_regex!r}"
    return None


def check(targets: list[Target], fetch: Fetch = fetch, attempts: int = 3, delay: float = 20) -> list[str]:
    failures: list[str] = []
    for target in targets:
        for attempt in range(attempts):
            problem = _problem(target, fetch)
            if problem is None or attempt == attempts - 1:
                break
            time.sleep(delay)
        if problem is not None:
            failures.append(problem)
    return failures


def main() -> int:
    targets = load_targets()
    failures = check(targets)
    for target in targets:
        print(f"checked {target.url}")
    for failure in failures:
        print(f"::error::{failure}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
