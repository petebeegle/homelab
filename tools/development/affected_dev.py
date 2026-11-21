#!/usr/bin/env python3
"""Which development-cluster Flux Kustomizations does a PR change?

Compares two checkouts (main and the PR head) by *rendered output*, not by file
paths: for every Flux Kustomization under kubernetes/clusters/development/{infra,apps},
it renders the Kustomization object itself and `kubectl kustomize <spec.path>` in
both trees. A Kustomization is affected when either differs, so a change reached
through a shared base, a patch or a cluster-level spec is found, and a change to a
production-only path is not. PR content is only rendered as data, never executed.

Changes to Flux's own components, the cluster-vars ConfigMap or the cluster
entrypoint are refused (`blocked`): the base smoke test applies child
Kustomizations only, and upgrading then downgrading Flux mid-test is its own risk.

Usage: affected_dev.py --base <main checkout> --head <PR checkout>  (changed paths on stdin)
Prints {"affected": [...], "blocked": str|null}.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Sequence

CLUSTER = "kubernetes/clusters/development"
CHILD_DIRS = ("infra", "apps")
BLOCKED_PREFIXES = (f"{CLUSTER}/flux-system/",)
BLOCKED_FILES = (f"{CLUSTER}/cluster-vars.yaml", f"{CLUSTER}/kustomization.yaml")
FLUX_KS = re.compile(r"(?m)^apiVersion: kustomize\.toolkit\.fluxcd\.io/v1\S*\nkind: Kustomization$")


@dataclass(frozen=True)
class Result:
    affected: list[str]
    blocked: str | None


def render(directory: Path) -> str:
    """`kubectl kustomize` output, or a stable error marker (a broken render is a difference too)."""
    if not (directory / "kustomization.yaml").exists():
        return f"MISSING {directory.name}"
    proc = subprocess.run(["kubectl", "kustomize", str(directory)], capture_output=True, text=True)
    if proc.returncode != 0:
        return "RENDER ERROR: " + proc.stderr.strip().splitlines()[-1] if proc.stderr.strip() else "RENDER ERROR"
    return proc.stdout


def documents(text: str) -> list[str]:
    return [doc.strip("\n") for doc in re.split(r"(?m)^---\n", text) if doc.strip()]


def flux_kustomizations(root: Path) -> dict[str, tuple[str, str]]:
    """name -> (the rendered Flux Kustomization document, its spec.path)."""
    found: dict[str, tuple[str, str]] = {}
    for child in CHILD_DIRS:
        for doc in documents(render(root / CLUSTER / child)):
            if not FLUX_KS.search(doc):
                continue
            name = re.search(r"(?m)^  name: (\S+)$", doc)
            path = re.search(r"(?m)^  path: (\S+)$", doc)
            if name and path:
                found[name.group(1)] = (doc, path.group(1).removeprefix("./"))
    return found


def blocked_reason(changed_files: Sequence[str]) -> str | None:
    for path in changed_files:
        if path.startswith(BLOCKED_PREFIXES) or path in BLOCKED_FILES:
            return f"changes the development cluster's Flux bootstrap or cluster-vars ({path}); validate by hand"
    return None


def affected(base: Path, head: Path, changed_files: Sequence[str]) -> Result:
    blocked = blocked_reason(changed_files)
    if blocked:
        return Result(affected=[], blocked=blocked)
    base_ks, head_ks = flux_kustomizations(base), flux_kustomizations(head)
    names: list[str] = []
    for name in sorted(set(base_ks) | set(head_ks)):
        if name not in base_ks or name not in head_ks:
            names.append(name)
            continue
        (base_doc, base_path), (head_doc, head_path) = base_ks[name], head_ks[name]
        if base_doc != head_doc or render(base / base_path) != render(head / head_path):
            names.append(name)
    return Result(affected=names, blocked=None)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--base", type=Path, required=True)
    parser.add_argument("--head", type=Path, required=True)
    args = parser.parse_args(argv)
    changed = [line.strip() for line in sys.stdin if line.strip()]
    print(json.dumps(asdict(affected(args.base, args.head, changed))))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
