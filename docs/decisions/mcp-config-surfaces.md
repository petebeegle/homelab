---
id: ADR-0010
status: accepted
scope:
  - mcp
  - codex
  - devcontainer
authority: binding
created: 2026-05-10
last_verified: 2026-05-10
supersedes: []
superseded_by:
---

# MCP Config Surfaces

## Decision

Use `.mcp.json` for general and devcontainer MCP clients, and use `.codex/config.toml` for the Codex runtime.

## Rationale

- Different clients read different MCP config formats.
- Codex-specific hook and MCP settings belong in `.codex/config.toml`.
- General MCP clients should not need to understand Codex hook configuration.

## Consequences

- Core MCP servers must stay consistent across both config files.
- The core shared server set is `kubernetes`, `terraform`, `grafana`, and `context7`.
- Do not keep unused MCP servers or legacy skill references in the repo.

## Operational Notes

- Update both config files when adding or changing a shared core MCP server.
- Use a policy check to catch drift between the two config surfaces.
