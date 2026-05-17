#!/usr/bin/env python3
"""Validate shared MCP server config consistency."""

from __future__ import annotations

import sys
import tomllib
from pathlib import Path
from typing import Any

TOOLS_LIB = Path(__file__).resolve().parents[2] / "tools" / "lib"
if str(TOOLS_LIB) not in sys.path:
    sys.path.insert(0, str(TOOLS_LIB))

from homelab_tools.jsonio import read_json
from homelab_tools.reporting import CheckResult


ROOT = Path(__file__).resolve().parents[2]
CORE_SERVERS = ("kubernetes", "terraform", "grafana", "context7")


def main() -> int:
    result = CheckResult("MCP config consistency check failed:")
    mcp_json = load_mcp_json(ROOT / ".mcp.json")
    codex_toml = load_codex_toml(ROOT / ".codex" / "config.toml")

    for server in CORE_SERVERS:
        if server not in mcp_json:
            result.add(f".mcp.json is missing core server {server}")
        if server not in codex_toml:
            result.add(f".codex/config.toml is missing core server {server}")
        if server in mcp_json and server in codex_toml:
            for field in ("command", "args"):
                if mcp_json[server].get(field) != codex_toml[server].get(field):
                    result.add(f"{server}: {field} differs between .mcp.json and .codex/config.toml")

    if not result.ok:
        result.print()
    return result.exit_code()


def load_mcp_json(path: Path) -> dict[str, dict[str, Any]]:
    data = read_json(path)
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
