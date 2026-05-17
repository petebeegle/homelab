"""Terraform relationship extraction."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import hcl2

from .kubernetes import read


def hcl_attr(text: str, key: str) -> str:
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        data = None
    if isinstance(data, dict) and key in data:
        return _clean_hcl_scalar(data[key])

    match = re.search(rf'(?m)^\s*{re.escape(key)}\s*=\s*"([^"]*)"', text)
    return match.group(1) if match else ""


def hcl_blocks(text: str, block_type: str) -> list[tuple[str, str]]:
    data = _load_hcl(text)
    raw_blocks = data.get(block_type, []) if isinstance(data, dict) else []
    if isinstance(raw_blocks, list):
        return [
            (name, json.dumps(body, sort_keys=True))
            for name, body in _iter_named_blocks(raw_blocks)
        ]

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


def terraform_relationships(terraform_roots: dict[str, Path]) -> list[str]:
    rows: list[str] = []
    for root_name, root in terraform_roots.items():
        main_path = root / "main.tf"
        if not main_path.exists():
            continue
        main = read(main_path)
        for name, body in hcl_blocks(main, "module"):
            source = hcl_attr(body, "source")
            deps = ", ".join(_module_refs(body)) or "(none)"
            rows.append(f"| `{root_name}` | Module | `{name}` | `{source}` | `{deps}` |")
        for name, body in hcl_blocks(main, "resource"):
            refs = ", ".join(sorted(set(_module_refs(body)))) or "(none)"
            rows.append(f"| `{root_name}` | Root resource | `{name}` | `(root)` | `{refs}` |")
    return sorted(rows)


def _load_hcl(text: str) -> dict[str, Any]:
    try:
        data = hcl2.loads(text)
    except Exception:
        return {}
    return data if isinstance(data, dict) else {}


def _iter_named_blocks(raw_blocks: list[Any]) -> list[tuple[str, dict[str, Any]]]:
    blocks: list[tuple[str, dict[str, Any]]] = []
    for item in raw_blocks:
        if not isinstance(item, dict):
            continue
        for first_label, first_value in item.items():
            first = _clean_hcl_label(first_label)
            if isinstance(first_value, dict) and _is_block_body(first_value):
                blocks.append((first, first_value))
                continue
            if not isinstance(first_value, dict):
                continue
            for second_label, body in first_value.items():
                if isinstance(body, dict):
                    blocks.append((f"{first}.{_clean_hcl_label(second_label)}", body))
    return blocks


def _is_block_body(value: dict[str, Any]) -> bool:
    return value.get("__is_block__") is True or any(
        not isinstance(child, dict) for child in value.values()
    )


def _module_refs(text: str) -> list[str]:
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        return re.findall(r"module\.([A-Za-z0-9_-]+)", text)
    return re.findall(r"module\.([A-Za-z0-9_-]+)", json.dumps(data))


def _clean_hcl_label(value: object) -> str:
    return _clean_hcl_scalar(value)


def _clean_hcl_scalar(value: object) -> str:
    if isinstance(value, str):
        stripped = value.strip()
        if stripped.startswith("${") and stripped.endswith("}"):
            stripped = stripped[2:-1]
        return stripped.strip('"')
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)
