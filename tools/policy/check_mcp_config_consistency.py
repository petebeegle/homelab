#!/usr/bin/env python3
"""Validate shared MCP server config consistency."""

from __future__ import annotations

import json
import sys
import tomllib
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
CORE_SERVERS = ("kubernetes", "terraform", "grafana", "context7")


def main() -> int:
    issues: list[str] = []
    mcp_json = load_mcp_json(ROOT / ".mcp.json")
    codex_toml = load_codex_toml(ROOT / ".codex" / "config.toml")

    for server in CORE_SERVERS:
        if server not in mcp_json:
            issues.append(f".mcp.json is missing core server {server}")
        if server not in codex_toml:
            issues.append(f".codex/config.toml is missing core server {server}")
        if server in mcp_json and server in codex_toml:
            for field in ("command", "args"):
                if mcp_json[server].get(field) != codex_toml[server].get(field):
                    issues.append(f"{server}: {field} differs between .mcp.json and .codex/config.toml")

    if issues:
        print("MCP config consistency check failed:", file=sys.stderr)
        for issue in issues:
            print(f"- {issue}", file=sys.stderr)
        return 1
    return 0


def load_mcp_json(path: Path) -> dict[str, dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    servers = data.get("mcpServers", {}).copy()
    for key, value in data.items():
        if key == "mcpServers":
            continue
        if isinstance(value, dict) and "command" in value:
            servers[key] = value
    return servers


def load_codex_toml(path: Path) -> dict[str, dict[str, Any]]:
    data = tomllib.loads(path.read_text(encoding="utf-8"))
    servers = data.get("mcp_servers", {})
    if not isinstance(servers, dict):
        return {}
    return servers


if __name__ == "__main__":
    raise SystemExit(main())
