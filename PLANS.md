# PLANS.md

## Codex Harness Documentation Migration

Status: implemented for the repository documentation surface.

Scope:

- Convert agent-facing guidance into Codex-neutral `AGENTS.md`.
- Remove the legacy compatibility pointer after agent workflows moved to `AGENTS.md`.
- Update README tooling references from tool-specific wording to agent-neutral wording.
- Convert selected legacy agent rules into decision records and runbooks under `docs/`.
- Leave legacy agent config, Codex config, devcontainer config, ignore rules, and `tools/agent-memory` to their dedicated workstreams.

Completed outputs:

- Agent guidance: `AGENTS.md`
- README agent tooling documentation
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
2. Decide whether legacy agent config should remain as source material or be removed after active workflows stop depending on it.

## Codex Harness PR Review Follow-Ups

Status: partially implemented by `terraform-apply-safety`.

Completed follow-ups:

1. `.codex/hooks/terraform_plan.sh` now fails closed when a selected Terraform directory is not initialized.
2. `.codex/hooks/terraform_plan.sh` now scopes `terraform -chdir=<dir> apply` and `terraform -chdir <dir> apply` checks to the targeted Terraform root.
3. `tools/agent-memory` now declares its pytest test dependency so `uv run --project tools/agent-memory pytest tools/agent-memory/tests` works without `--with pytest`.

Follow-up efforts:

1. No open follow-ups remain from this review set.
