"""Flux and Kustomize relationship extraction."""

from __future__ import annotations

from pathlib import Path

from .kubernetes import Manifest, kustomize_resources, list_maps, manifests_under, read, relative, scalar


def cluster_flux_kustomizations(root: Path, *, repo_root: Path) -> list[Manifest]:
    items = [
        item
        for item in manifests_under(root / "infra", root / "apps", repo_root=repo_root)
        if item.kind == "Kustomization"
    ]
    return sorted(items, key=lambda item: (item.relpath, item.name))


def flux_table(items: list[tuple[str, Manifest]]) -> list[str]:
    rows: list[str] = []
    for cluster, item in items:
        path_value = scalar(item.text, "path")
        depends = ", ".join(f"`{dep.get('name', '')}`" for dep in list_maps(item.text, "dependsOn")) or "(none)"
        substitution = ", ".join(ref.get("name", "") for ref in list_maps(item.text, "substituteFrom")) or "(none)"
        decrypts = "sops" if "decryption:" in item.text and "provider: sops" in item.text else "no"
        rows.append(
            f"| `{cluster}` | `{item.name}` | `{path_value}` | {depends} | `{substitution}` | `{decrypts}` |"
        )
    return rows


def kustomize_table(root: Path, *, repo_root: Path) -> list[str]:
    rows: list[str] = []
    for path in sorted(root.rglob("kustomization.yaml")):
        resources = kustomize_resources(path)
        if not resources:
            continue
        rows.append(
            f"| `{relative(path.parent, root=repo_root)}` | {', '.join(f'`{item}`' for item in resources)} |"
        )
    return rows
