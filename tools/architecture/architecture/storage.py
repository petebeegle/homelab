"""Storage and PVC relationship extraction."""

from __future__ import annotations

from pathlib import Path

from .kubernetes import Manifest, component, read, relative, scalar


def storage_relationships(manifests: list[Manifest], *, root: Path) -> list[str]:
    rows: set[str] = set()
    for item in manifests:
        if item.kind == "PersistentVolumeClaim":
            storage_class = scalar(item.text, "storageClassName")
            if storage_class:
                rows.add(f"| PVC | `{item.namespace}/{item.name}` | `{storage_class}` | `{item.relpath}` |")
        if item.kind == "HelmRelease" and "nfs-csi-storage" in item.text:
            rows.add(
                f"| HelmRelease values | `{item.namespace or 'default'}/{item.name}` | `nfs-csi-storage` | `{item.relpath}` |"
            )
    for path in sorted((root / "kubernetes").rglob("values.yaml")):
        text = read(path)
        if "nfs-csi-storage" in text:
            rows.add(
                f"| Values file | `{component(path, root=root)}` | `nfs-csi-storage` | `{relative(path, root=root)}` |"
            )
    return sorted(rows)
