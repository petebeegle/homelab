#!/usr/bin/env python3
"""Render the generated architecture relationship document."""

from __future__ import annotations

import argparse
import difflib
import re
import sys
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "docs" / "architecture.md"
PRODUCTION = ROOT / "kubernetes" / "clusters" / "production"
TERRAFORM_PRODUCTION = ROOT / "terraform" / "production"


@dataclass(frozen=True)
class Manifest:
    path: Path
    text: str
    kind: str
    name: str
    namespace: str

    @property
    def relpath(self) -> str:
        return self.path.relative_to(ROOT).as_posix()


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def relative(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


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


def manifests_under(*roots: Path) -> list[Manifest]:
    manifests: list[Manifest] = []
    for root in roots:
        for path in sorted(root.rglob("*.yaml")):
            text = read(path)
            for doc in split_documents(text):
                kind = scalar(doc, "kind")
                name = metadata_value(doc, "name")
                namespace = metadata_value(doc, "namespace")
                if kind and name:
                    manifests.append(Manifest(path, doc, kind, name, namespace))
    return manifests


def production_flux_kustomizations() -> list[Manifest]:
    items = [
        item
        for item in manifests_under(PRODUCTION / "infra", PRODUCTION / "apps")
        if item.kind == "Kustomization"
    ]
    return sorted(items, key=lambda item: (item.relpath, item.name))


def kustomize_resources(path: Path) -> list[str]:
    if not path.exists():
        return []
    return list_scalars(read(path), "resources")


def cluster_vars() -> list[tuple[str, str]]:
    path = PRODUCTION / "cluster-vars.yaml"
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


def component(path: Path) -> str:
    parts = path.relative_to(ROOT).parts
    if len(parts) >= 3 and parts[0] == "kubernetes" and parts[1] in {"apps", "infra"}:
        if parts[1] == "apps":
            return parts[2]
        if parts[2] in {"controllers", "monitoring", "network"} and len(parts) >= 4:
            return "/".join(parts[2:4])
        return parts[2]
    return path.parent.name


def gateway_routes(manifests: list[Manifest]) -> list[str]:
    rows: list[str] = []
    for item in manifests:
        if item.kind not in {"HTTPRoute", "TLSRoute"}:
            continue
        parents = list_maps(item.text, "parentRefs")
        parent = ", ".join(
            "/".join(
                part
                for part in [
                    ref.get("namespace") or item.namespace or "default",
                    ref.get("name", ""),
                    ref.get("sectionName", ""),
                ]
                if part
            )
            for ref in parents
        )
        hosts = ", ".join(list_scalars(item.text, "hostnames")) or "(none)"
        backends = ", ".join(
            f"{ref.get('name', '?')}:{ref.get('port', '?')}" for ref in list_maps(item.text, "backendRefs")
        )
        rows.append(
            f"| `{item.kind}` | `{item.namespace}/{item.name}` | `{hosts}` | `{parent or '(none)'}` | `{backends or '(none)'}` |"
        )
    return sorted(rows)


def storage_relationships(manifests: list[Manifest]) -> list[str]:
    rows: set[str] = set()
    for item in manifests:
        if item.kind == "PersistentVolumeClaim":
            storage_class = scalar(item.text, "storageClassName")
            if storage_class:
                rows.add(
                    f"| PVC | `{item.namespace}/{item.name}` | `{storage_class}` | `{item.relpath}` |"
                )
        if item.kind == "HelmRelease" and "nfs-csi-storage" in item.text:
            rows.add(
                f"| HelmRelease values | `{item.namespace or 'default'}/{item.name}` | `nfs-csi-storage` | `{item.relpath}` |"
            )
    for path in sorted((ROOT / "kubernetes").rglob("values.yaml")):
        text = read(path)
        if "nfs-csi-storage" in text:
            rows.add(f"| Values file | `{component(path)}` | `nfs-csi-storage` | `{relative(path)}` |")
    return sorted(rows)


def secret_relationships(manifests: list[Manifest]) -> list[str]:
    rows: list[str] = []
    for item in manifests:
        if item.kind != "Secret":
            continue
        encrypted = "yes" if "ENC[" in item.text or re.search(r"(?m)^sops:", item.text) else "unknown"
        rows.append(
            f"| `{component(item.path)}` | `{item.namespace or 'default'}/{item.name}` | `{encrypted}` | `{item.relpath}` |"
        )
    return sorted(rows)


def flux_table(items: list[Manifest]) -> list[str]:
    rows: list[str] = []
    for item in items:
        path_value = scalar(item.text, "path")
        depends = ", ".join(f"`{dep.get('name', '')}`" for dep in list_maps(item.text, "dependsOn")) or "(none)"
        substitution = ", ".join(ref.get("name", "") for ref in list_maps(item.text, "substituteFrom")) or "(none)"
        decrypts = "sops" if "decryption:" in item.text and "provider: sops" in item.text else "no"
        rows.append(
            f"| `{item.name}` | `{path_value}` | {depends} | `{substitution}` | `{decrypts}` |"
        )
    return rows


def kustomize_table(root: Path) -> list[str]:
    rows: list[str] = []
    for path in sorted(root.rglob("kustomization.yaml")):
        resources = kustomize_resources(path)
        if not resources:
            continue
        rows.append(f"| `{relative(path.parent)}` | {', '.join(f'`{item}`' for item in resources)} |")
    return rows


def hcl_attr(text: str, key: str) -> str:
    match = re.search(rf'(?m)^\s*{re.escape(key)}\s*=\s*"([^"]*)"', text)
    return match.group(1) if match else ""


def hcl_blocks(text: str, block_type: str) -> list[tuple[str, str]]:
    blocks: list[tuple[str, str]] = []
    lines = text.splitlines()
    index = 0
    pattern = re.compile(rf'^\s*{block_type}\s+"([^"]+)"(?:\s+"([^"]+)")?\s*\{{')
    while index < len(lines):
        match = pattern.match(lines[index])
        if not match:
            index += 1
            continue
        name = match.group(1) if match.group(2) is None else f"{match.group(1)}.{match.group(2)}"
        start = index
        depth = lines[index].count("{") - lines[index].count("}")
        index += 1
        while index < len(lines) and depth > 0:
            depth += lines[index].count("{") - lines[index].count("}")
            index += 1
        blocks.append((name, "\n".join(lines[start:index])))
    return blocks


def terraform_relationships() -> list[str]:
    main = read(TERRAFORM_PRODUCTION / "main.tf")
    rows: list[str] = []
    for name, body in hcl_blocks(main, "module"):
        source = hcl_attr(body, "source")
        deps = ", ".join(re.findall(r"module\.([A-Za-z0-9_-]+)", body)) or "(none)"
        rows.append(f"| Module | `{name}` | `{source}` | `{deps}` |")
    for name, body in hcl_blocks(main, "resource"):
        refs = ", ".join(sorted(set(re.findall(r"module\.([A-Za-z0-9_-]+)", body)))) or "(none)"
        rows.append(f"| Root resource | `{name}` | `(root)` | `{refs}` |")
    return sorted(rows)


def render() -> str:
    manifests = manifests_under(ROOT / "kubernetes")
    infra_flux = production_flux_kustomizations()
    app_flux = [item for item in infra_flux if "/apps/" in item.relpath]
    infra_flux = [item for item in infra_flux if "/infra/" in item.relpath]

    lines: list[str] = [
        "# Architecture",
        "",
        "<!-- GENERATED: do not edit by hand. Run `python3 tools/architecture/render.py --write`. -->",
        "",
        "This document is generated for agentic repo navigation. It records relationships that must stay aligned with the Kubernetes, Flux, and Terraform source of truth.",
        "",
        "## Cluster Entrypoint",
        "",
        f"- Production root Kustomization: `{relative(PRODUCTION / 'kustomization.yaml')}`.",
        f"- Root resources: {', '.join(f'`{item}`' for item in kustomize_resources(PRODUCTION / 'kustomization.yaml'))}.",
        f"- Infra activation list: {', '.join(f'`{item}`' for item in kustomize_resources(PRODUCTION / 'infra' / 'kustomization.yaml'))}.",
        f"- App activation list: {', '.join(f'`{item}`' for item in kustomize_resources(PRODUCTION / 'apps' / 'kustomization.yaml'))}.",
        "",
        "### Flux Substitution Variables",
        "",
        "| Variable | Value |",
        "| --- | --- |",
    ]
    lines.extend(f"| `{key}` | `{value}` |" for key, value in cluster_vars())

    lines.extend(
        [
            "",
            "## Flux Dependencies",
            "",
            "### Infrastructure",
            "",
            "| Kustomization | Path | Depends on | Substitute from | SOPS |",
            "| --- | --- | --- | --- | --- |",
        ]
    )
    lines.extend(flux_table(infra_flux))
    lines.extend(
        [
            "",
            "### Applications",
            "",
            "| Kustomization | Path | Depends on | Substitute from | SOPS |",
            "| --- | --- | --- | --- | --- |",
        ]
    )
    lines.extend(flux_table(app_flux))

    lines.extend(
        [
            "",
            "## Kustomize Resource Relationships",
            "",
            "| Component path | Listed resources |",
            "| --- | --- |",
        ]
    )
    lines.extend(kustomize_table(ROOT / "kubernetes" / "infra"))
    lines.extend(kustomize_table(ROOT / "kubernetes" / "apps"))

    lines.extend(
        [
            "",
            "## Gateway Routes",
            "",
            "| Kind | Route | Hostnames | Parent Gateway | Backend refs |",
            "| --- | --- | --- | --- | --- |",
        ]
    )
    lines.extend(gateway_routes(manifests))

    lines.extend(
        [
            "",
            "## Storage Relationships",
            "",
            "| Source | Owner | StorageClass | Path |",
            "| --- | --- | --- | --- |",
        ]
    )
    lines.extend(storage_relationships(manifests))

    lines.extend(
        [
            "",
            "## Secret Manifests",
            "",
            "This lists secret manifest presence only. Secret values are not rendered.",
            "",
            "| Component | Secret | SOPS encrypted | Path |",
            "| --- | --- | --- | --- |",
        ]
    )
    lines.extend(secret_relationships(manifests))

    lines.extend(
        [
            "",
            "## Terraform Substrate",
            "",
            "| Type | Name | Source | References |",
            "| --- | --- | --- | --- |",
        ]
    )
    lines.extend(terraform_relationships())
    lines.append("")
    return "\n".join(lines)


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
