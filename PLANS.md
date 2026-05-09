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

## Codex Harness PR Review Follow-Ups

Status: identified during final read-only review of branch `harness` against `origin/main`.

Follow-up efforts:

1. Make `.codex/hooks/terraform_plan.sh` fail closed when a Terraform directory is not initialized, instead of skipping every uninitialized directory and potentially allowing `terraform apply` without a successful plan.
2. Narrow `.codex/hooks/terraform_plan.sh` planning scope so targeted `terraform apply` commands are not blocked by unrelated Terraform workspaces with missing credentials or unrelated drift.
3. Declare the memory-agent test runner dependency, or document the supported command, so `uv run --project tools/agent-memory pytest tools/agent-memory/tests` works without adding `--with pytest`.
4. Decide whether current local `graphify-out/` changes should be refreshed and committed deliberately or discarded before merge, so generated graph artifacts are not accidentally staged.
