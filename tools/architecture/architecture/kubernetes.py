"""Kubernetes manifest extraction helpers for the architecture renderer."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


@dataclass(frozen=True)
class Manifest:
    path: Path
    text: str
    kind: str
    name: str
    namespace: str
    root: Path = field(default_factory=lambda: Path(__file__).resolve().parents[3])

    @property
    def relpath(self) -> str:
        return self.path.relative_to(self.root).as_posix()


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def relative(path: Path, *, root: Path) -> str:
    return path.relative_to(root).as_posix()


def split_documents(text: str) -> list[str]:
    documents: list[str] = []
    for doc in re.split(r"(?m)^---\s*$", text):
        if not doc.strip():
            continue
        if _load_yaml_document(doc):
            documents.append(doc.strip())
    return documents


def scalar(text: str, key: str) -> str:
    value = _find_key(_load_yaml_document(text), key)
    if isinstance(value, (dict, list)) or value is None:
        return ""
    return _scalar_text(value)


def metadata_value(text: str, key: str) -> str:
    metadata = _find_key(_load_yaml_document(text), "metadata")
    if not isinstance(metadata, dict):
        return ""
    value = metadata.get(key)
    if isinstance(value, (dict, list)) or value is None:
        return ""
    return _scalar_text(value)


def lines_after(lines: list[str], key: str) -> list[str]:
    for index, line in enumerate(lines):
        if line.strip() in {f"{key}:", f"- {key}:"}:
            indent = len(line) - len(line.lstrip())
            block: list[str] = []
            for child in lines[index + 1 :]:
                if not child.strip():
                    continue
                child_indent = len(child) - len(child.lstrip())
                if child_indent <= indent:
                    break
                block.append(child)
            return block
    return []


def list_scalars(text: str, key: str) -> list[str]:
    value = _find_key(_load_yaml_document(text), key)
    if not isinstance(value, list):
        return []
    return [_scalar_text(item) for item in value if not isinstance(item, (dict, list)) and item is not None]


def list_maps(text: str, key: str) -> list[dict[str, str]]:
    value = _find_key(_load_yaml_document(text), key)
    if not isinstance(value, list):
        return []
    items: list[dict[str, str]] = []
    for item in value:
        if not isinstance(item, dict):
            continue
        items.append(
            {
                _scalar_text(map_key): _scalar_text(map_value)
                for map_key, map_value in item.items()
                if not isinstance(map_value, (dict, list)) and map_value is not None
            }
        )
    return items


def manifests_under(*roots: Path, repo_root: Path) -> list[Manifest]:
    manifests: list[Manifest] = []
    for root in roots:
        for path in sorted(root.rglob("*.yaml")):
            text = read(path)
            for doc in split_documents(text):
                kind = scalar(doc, "kind")
                name = metadata_value(doc, "name")
                namespace = metadata_value(doc, "namespace")
                if kind and name:
                    manifests.append(Manifest(path, doc, kind, name, namespace, repo_root))
    return manifests


def kustomize_resources(path: Path) -> list[str]:
    if not path.exists():
        return []
    return list_scalars(read(path), "resources")


def cluster_vars(root: Path) -> list[tuple[str, str]]:
    path = root / "cluster-vars.yaml"
    if not path.exists():
        return []
    data = _load_yaml_document(read(path))
    values = data.get("data") if isinstance(data, dict) else None
    if not isinstance(values, dict):
        return []
    return sorted((_scalar_text(key), _scalar_text(value)) for key, value in values.items())


def component(path: Path, *, root: Path) -> str:
    parts = path.relative_to(root).parts
    if len(parts) >= 3 and parts[0] == "kubernetes" and parts[1] in {"apps", "infra"}:
        if parts[1] == "apps":
            return parts[2]
        if parts[2] in {"controllers", "monitoring", "network"} and len(parts) >= 4:
            return "/".join(parts[2:4])
        return parts[2]
    return path.parent.name


def secret_relationships(manifests: list[Manifest], *, root: Path) -> list[str]:
    rows: list[str] = []
    for item in manifests:
        if item.kind != "Secret":
            continue
        encrypted = "yes" if "ENC[" in item.text or re.search(r"(?m)^sops:", item.text) else "unknown"
        rows.append(
            f"| `{component(item.path, root=root)}` | `{item.namespace or 'default'}/{item.name}` | `{encrypted}` | `{item.relpath}` |"
        )
    return sorted(rows)


def _load_yaml_document(text: str) -> Any:
    try:
        return yaml.safe_load(text) or {}
    except yaml.YAMLError:
        return {}


def _find_key(value: Any, key: str) -> Any:
    if isinstance(value, dict):
        if key in value:
            return value[key]
        for child in value.values():
            found = _find_key(child, key)
            if found is not None:
                return found
    elif isinstance(value, list):
        for child in value:
            found = _find_key(child, key)
            if found is not None:
                return found
    return None


def _scalar_text(value: object) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value).strip().strip('"')
