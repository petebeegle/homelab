"""Kubernetes manifest extraction helpers for the architecture renderer."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path


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
    return [doc.strip() for doc in re.split(r"(?m)^---\s*$", text) if doc.strip()]


def scalar(text: str, key: str) -> str:
    match = re.search(rf"(?m)^\s*{re.escape(key)}:\s*(.+?)\s*$", text)
    if not match:
        return ""
    return match.group(1).strip().strip('"')


def metadata_value(text: str, key: str) -> str:
    match = re.search(r"(?ms)^metadata:\n(?P<body>(?:  .+\n?)*)", text)
    if not match:
        return ""
    return scalar(match.group("body"), key)


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
    values: list[str] = []
    for line in lines_after(text.splitlines(), key):
        stripped = line.strip()
        if stripped.startswith("- "):
            values.append(stripped[2:].strip().strip('"'))
    return values


def list_maps(text: str, key: str) -> list[dict[str, str]]:
    items: list[dict[str, str]] = []
    current: dict[str, str] | None = None
    for line in lines_after(text.splitlines(), key):
        stripped = line.strip()
        if stripped.startswith("- "):
            if current:
                items.append(current)
            current = {}
            stripped = stripped[2:].strip()
            if ":" in stripped:
                k, v = stripped.split(":", 1)
                current[k.strip()] = v.strip().strip('"')
        elif current is not None and ":" in stripped:
            k, v = stripped.split(":", 1)
            current[k.strip()] = v.strip().strip('"')
    if current:
        items.append(current)
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
    text = read(path)
    body = re.search(r"(?ms)^data:\n(?P<body>(?:  .+\n?)*)", text)
    if not body:
        return []
    values: list[tuple[str, str]] = []
    for line in body.group("body").splitlines():
        stripped = line.strip()
        if ":" not in stripped:
            continue
        key, value = stripped.split(":", 1)
        values.append((key.strip(), value.strip().strip('"')))
    return sorted(values)


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
