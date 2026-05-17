#!/usr/bin/env python3
"""Render the generated architecture relationship document."""

from __future__ import annotations

import argparse
import difflib
import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from architecture.flux import cluster_flux_kustomizations as _cluster_flux_kustomizations
from architecture.flux import flux_table, kustomize_table as _kustomize_table
from architecture.gateway import gateway_routes
from architecture.kubernetes import (
    Manifest,
    cluster_vars,
    component as _component,
    kustomize_resources,
    lines_after,
    list_maps,
    list_scalars,
    manifests_under as _manifests_under,
    metadata_value,
    read,
    relative as _relative,
    scalar,
    secret_relationships as _secret_relationships,
    split_documents,
)
from architecture.markdown import render as _render
from architecture.storage import storage_relationships as _storage_relationships
from architecture.terraform import hcl_attr, hcl_blocks
from architecture.terraform import terraform_relationships as _terraform_relationships


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "docs" / "architecture.md"
CLUSTERS = {
    "production": ROOT / "kubernetes" / "clusters" / "production",
    "development": ROOT / "kubernetes" / "clusters" / "development",
}
TERRAFORM_ROOTS = {
    "production": ROOT / "terraform" / "production",
    "development": ROOT / "terraform" / "development",
}


def relative(path: Path) -> str:
    return _relative(path, root=ROOT)


def manifests_under(*roots: Path) -> list[Manifest]:
    return _manifests_under(*roots, repo_root=ROOT)


def cluster_flux_kustomizations(root: Path) -> list[Manifest]:
    return _cluster_flux_kustomizations(root, repo_root=ROOT)


def component(path: Path) -> str:
    return _component(path, root=ROOT)


def storage_relationships(manifests: list[Manifest]) -> list[str]:
    return _storage_relationships(manifests, root=ROOT)


def secret_relationships(manifests: list[Manifest]) -> list[str]:
    return _secret_relationships(manifests, root=ROOT)


def kustomize_table(root: Path) -> list[str]:
    return _kustomize_table(root, repo_root=ROOT)


def terraform_relationships() -> list[str]:
    return _terraform_relationships(TERRAFORM_ROOTS)


def render() -> str:
    return _render(root=ROOT, clusters=CLUSTERS, terraform_roots=TERRAFORM_ROOTS)


def check(expected: str) -> int:
    if not OUTPUT.exists():
        print(f"{relative(OUTPUT)} is missing. Run: python3 tools/architecture/render.py --write", file=sys.stderr)
        return 1
    actual = read(OUTPUT)
    if actual == expected:
        return 0
    diff = difflib.unified_diff(
        actual.splitlines(),
        expected.splitlines(),
        fromfile=relative(OUTPUT),
        tofile="generated",
        lineterm="",
    )
    print(f"{relative(OUTPUT)} is stale. Run: python3 tools/architecture/render.py --write", file=sys.stderr)
    print("\n".join(diff), file=sys.stderr)
    return 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true", help="write docs/architecture.md")
    group.add_argument("--check", action="store_true", help="fail if docs/architecture.md is stale")
    args = parser.parse_args()

    output = render()
    if args.write:
        OUTPUT.write_text(output, encoding="utf-8")
        return 0
    return check(output)


if __name__ == "__main__":
    raise SystemExit(main())
