#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_INVENTORY = Path(__file__).with_name("production_items.json")
DEFAULT_OUTPUT = REPO_ROOT / "kubernetes/clusters/production/onepassword-items"
ID_PATTERN = re.compile(r"^[a-z0-9]{26}$")
NAME_PATTERN = re.compile(r"^[a-z0-9](?:[-a-z0-9.]*[a-z0-9])?$")
KEY_PATTERN = re.compile(r"^[-._a-zA-Z0-9]+$")


def load_inventory(path: Path) -> dict[str, Any]:
    inventory = json.loads(path.read_text(encoding="utf-8"))
    items = inventory.get("items")
    if inventory.get("schema_version") != 1 or not isinstance(items, list):
        raise ValueError("inventory schema is invalid")
    expected_count = inventory.get("expected_count", 17)
    if not isinstance(expected_count, int) or expected_count <= 0:
        raise ValueError("inventory expected_count is invalid")
    if len(items) != expected_count:
        raise ValueError(
            f"inventory must contain {expected_count} items, found {len(items)}"
        )

    pairs: set[tuple[str, str]] = set()
    generated: set[tuple[str, str]] = set()
    titles: set[str] = set()
    for item in items:
        pair = (item["namespace"], item["legacy_name"])
        generated_pair = (item["namespace"], item["generated_name"])
        title = item["item_title"]
        expected_title = f"k8s--{item['namespace']}--{item['legacy_name']}"
        if pair in pairs or generated_pair in generated or title in titles:
            raise ValueError("inventory contains a duplicate identity")
        pairs.add(pair)
        generated.add(generated_pair)
        titles.add(title)
        if title != expected_title:
            raise ValueError(f"item title convention mismatch for {item['namespace']}/{item['legacy_name']}")
        if item["generated_name"] != f"{item['legacy_name']}-onepassword":
            raise ValueError(f"generated name convention mismatch for {item['namespace']}/{item['legacy_name']}")
        if not NAME_PATTERN.fullmatch(item["namespace"]) or not NAME_PATTERN.fullmatch(item["generated_name"]):
            raise ValueError(f"invalid Kubernetes identity for {title}")
        keys = item.get("keys")
        if not isinstance(keys, list) or not keys or keys != sorted(set(keys)):
            raise ValueError(f"keys must be a non-empty sorted unique list for {title}")
        if any(not KEY_PATTERN.fullmatch(key) for key in keys):
            raise ValueError(f"invalid Kubernetes Secret key in inventory for {title}")
        if item["type"] not in {"Opaque", "kubernetes.io/basic-auth"}:
            raise ValueError(f"unsupported Secret type for {title}")
    return inventory


def validate_id(kind: str, value: Any) -> str:
    if not isinstance(value, str) or not ID_PATTERN.fullmatch(value):
        raise ValueError(f"{kind} ID is invalid")
    return value


def validate_item_metadata(title: str, item_json: dict[str, Any], expected: set[str]) -> str:
    item_id = validate_id("item", item_json.get("id"))
    labels: list[str] = []
    for field in item_json.get("fields") or []:
        value = field.get("value")
        if value is None or value == "":
            continue
        label = field.get("label") or field.get("id")
        if not isinstance(label, str):
            raise ValueError(f"field label is invalid for {title}")
        labels.append(label)
    populated_urls = [url for url in item_json.get("urls") or [] if url.get("href")]
    files = item_json.get("files") or []
    if populated_urls or files:
        raise ValueError(f"URL/file fields are not allowed for {title}")
    if len(labels) != len(set(labels)):
        raise ValueError(f"duplicate non-empty field label for {title}")
    if set(labels) != expected:
        raise ValueError(
            f"field set mismatch for {title}: expected {len(expected)}, observed {len(labels)}"
        )
    return item_id


def render_item(item: dict[str, Any], vault_id: str, item_id: str) -> str:
    validate_id("vault", vault_id)
    validate_id("item", item_id)
    return f'''---
apiVersion: onepassword.com/v1
kind: OnePasswordItem
metadata:
  name: {item["generated_name"]}
  namespace: {item["namespace"]}
  labels:
    app.kubernetes.io/managed-by: onepassword-operator
    homelab.petebeegle.com/legacy-secret: {item["legacy_name"]}
type: {item["type"]}
spec:
  itemPath: "vaults/{vault_id}/items/{item_id}"
'''


def run_json(command: list[str], *, failure_context: str | None = None) -> dict[str, Any]:
    result = subprocess.run(command, text=True, capture_output=True, check=False)
    if result.returncode != 0:
        context = failure_context or f"{command[0]} {command[1]} command failed"
        raise RuntimeError(f"{context}; captured command output suppressed")
    try:
        value = json.loads(result.stdout)
    except json.JSONDecodeError as error:
        raise RuntimeError(f"command returned invalid JSON: {command[0]} {command[1]}") from error
    if not isinstance(value, dict):
        raise RuntimeError(f"command returned unexpected JSON: {command[0]} {command[1]}")
    return value


def resolve(inventory: dict[str, Any], vault: str) -> tuple[str, list[tuple[dict[str, Any], str]]]:
    if shutil.which("op") is None:
        raise RuntimeError("1Password CLI is required")
    vault_json = run_json(["op", "vault", "get", vault, "--format=json"])
    vault_id = validate_id("vault", vault_json.get("id"))
    resolved: list[tuple[dict[str, Any], str]] = []
    for item in inventory["items"]:
        title = item["item_title"]
        item_json = run_json(
            ["op", "item", "get", title, "--vault", vault, "--format=json"],
            failure_context=f"item lookup failed for {title}",
        )
        item_id = validate_item_metadata(title, item_json, set(item["keys"]))
        resolved.append((item, item_id))
    return vault_id, resolved


def write_manifests(output_dir: Path, vault_id: str, resolved: list[tuple[dict[str, Any], str]]) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    expected_files: set[str] = set()
    for item, item_id in resolved:
        filename = f"{item['namespace']}--{item['generated_name']}.yaml"
        expected_files.add(filename)
        (output_dir / filename).write_text(render_item(item, vault_id, item_id), encoding="utf-8")
    expected_files.add("kustomization.yaml")
    unexpected = {
        path.name for path in output_dir.glob("*.yaml") if path.name not in expected_files
    }
    if unexpected:
        raise RuntimeError(f"output directory contains {len(unexpected)} unexpected YAML file(s)")
    resources = "\n".join(
        f"  - {name}" for name in sorted(expected_files - {"kustomization.yaml"})
    )
    (output_dir / "kustomization.yaml").write_text(
        "---\napiVersion: kustomize.config.k8s.io/v1beta1\nkind: Kustomization\nresources:\n"
        + resources
        + "\n",
        encoding="utf-8",
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Resolve production 1Password item IDs and render ID-only Kubernetes resources")
    parser.add_argument("--inventory", type=Path, default=DEFAULT_INVENTORY)
    parser.add_argument("--vault", default="cluster production")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check-only", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        inventory = load_inventory(args.inventory)
        vault_id, resolved = resolve(inventory, args.vault)
        if not args.check_only:
            write_manifests(args.output_dir, vault_id, resolved)
    except (OSError, ValueError, RuntimeError) as error:
        print(f"1Password item resolution failed: {error}", file=sys.stderr)
        return 1
    action = "validated" if args.check_only else "rendered"
    print(f"Production 1Password items {action}: {len(resolved)} ID-only resources")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
