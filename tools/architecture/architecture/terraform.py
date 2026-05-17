"""Regex-based Terraform relationship extraction."""

from __future__ import annotations

import re
from pathlib import Path

from .kubernetes import read


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


def terraform_relationships(terraform_roots: dict[str, Path]) -> list[str]:
    rows: list[str] = []
    for root_name, root in terraform_roots.items():
        main_path = root / "main.tf"
        if not main_path.exists():
            continue
        main = read(main_path)
        for name, body in hcl_blocks(main, "module"):
            source = hcl_attr(body, "source")
            deps = ", ".join(re.findall(r"module\.([A-Za-z0-9_-]+)", body)) or "(none)"
            rows.append(f"| `{root_name}` | Module | `{name}` | `{source}` | `{deps}` |")
        for name, body in hcl_blocks(main, "resource"):
            refs = ", ".join(sorted(set(re.findall(r"module\.([A-Za-z0-9_-]+)", body)))) or "(none)"
            rows.append(f"| `{root_name}` | Root resource | `{name}` | `(root)` | `{refs}` |")
    return sorted(rows)
