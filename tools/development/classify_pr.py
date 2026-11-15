#!/usr/bin/env python3
"""Decide whether a PR can be smoke-tested in the dev cluster.

Reads changed file paths on stdin (one per line) and prints one JSON object:
{"tested": bool, "app": str|null, "browser": bool, "reason": str}.

A PR is *tested* only when every changed file is under one profiled app's
directory (`kubernetes/apps/<app>/`), that app's smoke profile opts in with
`prSmoke`, and nothing under terraform/, tests/browser/ or tools/development/
changed (the check runs the verifier from main, so changes to it would not be
exercised). Anything else is *not tested*, with the reason.
"""

from __future__ import annotations

import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Mapping, Sequence

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from devverify.profiles import load_smoke_profiles  # noqa: E402

APPS_PREFIX = "kubernetes/apps/"
VERIFIER_PREFIXES = ("tests/browser/", "tools/development/")


@dataclass(frozen=True)
class Classification:
    tested: bool
    app: str | None
    browser: bool
    reason: str


def _not_tested(reason: str) -> Classification:
    return Classification(tested=False, app=None, browser=False, reason=reason)


def classify(changed_files: Sequence[str], profiles: Mapping[str, object]) -> Classification:
    if not changed_files:
        return _not_tested("no changes")
    for path in changed_files:
        if path.startswith("terraform/"):
            return _not_tested(f"changes terraform ({path}); run the dev smoke by hand")
        if path.startswith(VERIFIER_PREFIXES):
            return _not_tested(f"changes the verifier or its browser tests ({path}); the check runs the verifier from main")
    apps: set[str] = set()
    for path in changed_files:
        if not path.startswith(APPS_PREFIX) or path.count("/") < 3:
            return _not_tested(f"changes files outside a profiled app: {path}")
        apps.add(path[len(APPS_PREFIX):].split("/", 1)[0])
    if len(apps) > 1:
        return _not_tested(f"multiple apps: {', '.join(sorted(apps))}")
    (app,) = apps
    profile = profiles.get(app)
    if profile is None or not getattr(profile, "pr_smoke", False):
        return _not_tested(f"app {app} has no PR smoke profile")
    return Classification(tested=True, app=app, browser=getattr(profile, "browser", None) is not None, reason="ok")


def main() -> int:
    files = [line.strip() for line in sys.stdin if line.strip()]
    print(json.dumps(asdict(classify(files, load_smoke_profiles()))))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
