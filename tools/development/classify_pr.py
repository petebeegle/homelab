#!/usr/bin/env python3
"""Decide whether a PR can be smoke-tested in the dev cluster.

Reads changed file paths on stdin (one per line) and prints one JSON object:
{"tested": bool, "app": str|null, "browser": bool, "reason": str, "automerge": bool}.

A PR is *tested* only when every changed file is under one profiled app's
directory (`kubernetes/apps/<app>/`), that app's smoke profile opts in with
`prSmoke`, and nothing under terraform/, tests/browser/ or tools/development/
changed (the check runs the verifier from main, so changes to it would not be
exercised). Anything else is *not tested*, with the reason.

`automerge` says every changed file is inside Renovate's auto-merge paths
(renovate.json). Those paths are all deployed by development, so the aggregator
fails a Renovate PR that is inside them yet was not tested (two apps in one PR,
say) rather than let Renovate merge it on a green "not tested".
"""

from __future__ import annotations

import json
import sys
from dataclasses import asdict, dataclass, replace
from pathlib import Path
from typing import Mapping, Sequence

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from devverify.profiles import load_smoke_profiles  # noqa: E402

REPO_ROOT = SCRIPT_DIR.parents[1]
APPS_PREFIX = "kubernetes/apps/"
VERIFIER_PREFIXES = ("tests/browser/", "tools/development/")


@dataclass(frozen=True)
class Classification:
    tested: bool
    app: str | None
    browser: bool
    reason: str
    automerge: bool = False


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


def automerge_prefixes(renovate: Path = REPO_ROOT / "renovate.json") -> tuple[str, ...]:
    """Directory prefixes of Renovate's auto-merge rules (each pattern is `<dir>/**`)."""
    config = json.loads(renovate.read_text(encoding="utf-8"))
    prefixes = []
    for rule in config.get("packageRules", []):
        if rule.get("automerge") is not True:
            continue
        for pattern in rule.get("matchFileNames", []):
            if not pattern.endswith("/**") or any(c in pattern[:-3] for c in "*?[{"):
                raise ValueError(f"auto-merge pattern must be a whole directory, <dir>/**: {pattern}")
            prefixes.append(pattern[:-2])
    return tuple(prefixes)


def within_automerge_paths(changed_files: Sequence[str], prefixes: Sequence[str]) -> bool:
    return bool(changed_files) and bool(prefixes) and all(path.startswith(tuple(prefixes)) for path in changed_files)


def main() -> int:
    files = [line.strip() for line in sys.stdin if line.strip()]
    result = classify(files, load_smoke_profiles())
    result = replace(result, automerge=within_automerge_paths(files, automerge_prefixes()))
    print(json.dumps(asdict(result)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
