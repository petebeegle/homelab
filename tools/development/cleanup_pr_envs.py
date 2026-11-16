#!/usr/bin/env python3
"""Delete leftover PR smoke environments from the dev cluster.

A cancelled workflow can die before its cleanup runs, so each smoke run starts by
removing its own slug (`--slug pr-12`), and a scheduled job removes anything older
than a threshold (`--older-than 3h`). Only objects named for a `pr-<number>` slug
are ever considered: `branch-<app>-pr-<N>` Kustomizations and `branch-pr-<N>`
GitRepositories in flux-system.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from devverify.config import FLUX_NAMESPACE, VerificationError, parse_duration  # noqa: E402
from devverify.kube import run_command  # noqa: E402

SLUG = re.compile(r"^pr-[0-9]+$")
KUSTOMIZATION = "kustomization.kustomize.toolkit.fluxcd.io"
GITREPOSITORY = "gitrepository.source.toolkit.fluxcd.io"
KUSTOMIZATION_NAME = re.compile(r"^branch-(?P<app>[a-z0-9]+(?:-[a-z0-9]+)*?)-(?P<slug>pr-[0-9]+)$")
GITREPOSITORY_NAME = re.compile(r"^branch-(?P<slug>pr-[0-9]+)$")
TIMEOUT = parse_duration("5m")


def _kubectl(kubeconfig: Path, *args: str) -> list[str]:
    return ["kubectl", "--kubeconfig", str(kubeconfig), *args]


def _age_seconds(item: dict, now: datetime) -> float:
    created = datetime.strptime(item["metadata"]["creationTimestamp"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    return (now - created).total_seconds()


def cleanup_pr_envs(
    *,
    kubeconfig: Path,
    slug: str | None = None,
    older_than_seconds: int | None = None,
    runner=subprocess.run,
    now: datetime | None = None,
) -> list[str]:
    if (slug is None) == (older_than_seconds is None):
        raise ValueError("give exactly one of slug and older_than_seconds")
    if slug is not None and not SLUG.fullmatch(slug):
        raise ValueError("slug must look like pr-<number>")
    if older_than_seconds is not None and older_than_seconds <= 0:
        raise ValueError("older_than_seconds must be positive")
    now = now or datetime.now(timezone.utc)

    listing = run_command(
        _kubectl(kubeconfig, "-n", FLUX_NAMESPACE, "get", f"{KUSTOMIZATION},{GITREPOSITORY}", "-o", "json"),
        runner=runner,
        timeout=TIMEOUT,
        capture_output=True,
    )
    try:
        items = json.loads(listing.stdout)["items"]
    except (ValueError, KeyError, TypeError) as exc:
        raise VerificationError("could not read Flux objects") from exc

    def selected(item: dict, found_slug: str) -> bool:
        if slug is not None:
            return found_slug == slug
        return _age_seconds(item, now) >= older_than_seconds

    kustomizations: list[tuple[str, str]] = []  # (name, namespace)
    gitrepositories: list[str] = []
    for item in items:
        name = item["metadata"]["name"]
        if item.get("kind") == "Kustomization" and (match := KUSTOMIZATION_NAME.fullmatch(name)):
            if selected(item, match["slug"]):
                kustomizations.append((name, f"{match['app']}-{match['slug']}"))
        elif item.get("kind") == "GitRepository" and (match := GITREPOSITORY_NAME.fullmatch(name)):
            if selected(item, match["slug"]):
                gitrepositories.append(name)

    deleted: list[str] = []
    for name, namespace in kustomizations:
        run_command(
            _kubectl(kubeconfig, "-n", FLUX_NAMESPACE, "delete", f"{KUSTOMIZATION}/{name}",
                     "--ignore-not-found=true", "--wait=true", f"--timeout={TIMEOUT.raw}"),
            runner=runner,
            timeout=TIMEOUT,
        )
        run_command(
            _kubectl(kubeconfig, "wait", f"namespace/{namespace}", "--for=delete", f"--timeout={TIMEOUT.raw}"),
            runner=runner,
            timeout=TIMEOUT,
        )
        deleted.append(f"kustomization/{name}")
    for name in gitrepositories:
        run_command(
            _kubectl(kubeconfig, "-n", FLUX_NAMESPACE, "delete", f"{GITREPOSITORY}/{name}",
                     "--ignore-not-found=true", "--wait=true", f"--timeout={TIMEOUT.raw}"),
            runner=runner,
            timeout=TIMEOUT,
        )
        deleted.append(f"gitrepository/{name}")
    return deleted


def main(argv=None, *, runner=subprocess.run) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--kubeconfig", required=True, type=Path)
    selector = parser.add_mutually_exclusive_group(required=True)
    selector.add_argument("--slug", help="delete this slug's environment, e.g. pr-12")
    selector.add_argument("--older-than", type=parse_duration, help="delete every pr-* environment older than this, e.g. 3h")
    args = parser.parse_args(argv)
    try:
        deleted = cleanup_pr_envs(
            kubeconfig=args.kubeconfig,
            slug=args.slug,
            older_than_seconds=args.older_than.seconds if args.older_than else None,
            runner=runner,
        )
    except (ValueError, VerificationError) as exc:
        print(f"cleanup failed: {exc}", file=sys.stderr)
        return 1
    for name in deleted:
        print(f"deleted {name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
