# PLANS.md

## Codex Harness Documentation Migration

Status: implemented for the repository documentation surface.

Scope:

- Convert agent-facing guidance from `CLAUDE.md` into Codex-neutral `AGENTS.md`.
- Keep `CLAUDE.md` as a compatibility pointer for agents or tools that still discover that filename.
- Convert selected legacy agent rules into decision records and runbooks under `docs/`.
- Leave legacy agent config, Codex config, devcontainer config, ignore rules, and `tools/agent-memory` to their dedicated workstreams.

Completed outputs:

- Agent guidance: `AGENTS.md`
- Compatibility pointer: `CLAUDE.md`
- Decision records:
  - `docs/decisions/flux-gitops-source-of-truth.md`
  - `docs/decisions/cilium-gateway-api-ingress.md`
  - `docs/decisions/sops-age-secrets.md`
  - `docs/decisions/mcp-tool-routing.md`
  - `docs/decisions/synology-nfs-storage.md`
  - `docs/decisions/talos-management-boundaries.md`
  - `docs/decisions/agent-memory-compaction.md`
- Runbooks:
  - `docs/runbooks/add-app.md`
  - `docs/runbooks/add-secret.md`
  - `docs/runbooks/diagnose-kustomization.md`
  - `docs/runbooks/diagnose-helmrelease.md`
  - `docs/runbooks/upgrade-talos.md`

Follow-up candidates:

1. Move useful older top-level `runbooks/` content into `docs/runbooks/` in a separate change.
2. Update README references from tool-specific wording to agent-neutral wording in a separate change.
3. Decide whether legacy agent config should remain as source material or be removed after active workflows stop depending on it.
