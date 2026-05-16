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

## Monitoring Radar Grafana Dashboard

Status: planned. Implementation discovery and live validation are blocked until Grafana MCP is reloaded or otherwise usable from the current Codex session.

Summary:

- Add an overview Grafana dashboard that acts as the homelab monitoring radar: the first port of call for cluster visibility, high-level diagnosis, and drill-down into specialized dashboards.
- Keep the dashboard broad and shallow. It should answer "what needs attention now?" before sending the operator to Kubernetes, Flux, observability, Proxmox, synthetics, app, or log-focused views.

Key changes:

- Manage the dashboard through GitOps as dashboard JSON plus the existing Grafana Operator wrapper pattern.
- Provision it in the existing `Monitoring` Grafana folder.
- Make it Grafana Home by setting `dashboards.default_home_dashboard_path` in the Grafana Helm values.
- Include links to existing specialized dashboards so this page is a navigation hub, not a replacement for detailed views.
- Use high-level panels for Kubernetes health, Flux reconciliation, observability stack health, certificates, Gateway/Cilium traffic and errors, storage, synthetics, important apps, capacity, and log triage.

Interfaces/config:

- Follow the existing `GrafanaDashboard` plus ConfigMap pattern under `kubernetes/infra/monitoring/grafana/dashboards/`.
- Update Grafana Helm values in `kubernetes/infra/monitoring/grafana/app.yaml` for the Home dashboard path.
- Use existing datasource UIDs `prometheus` and `loki`.
- Proposed dashboard identity: UID `monitoring-radar`, title `Monitoring Radar`.

Test plan:

- Validate dashboard JSON with `jq`.
- Render the relevant kustomization with `kustomize`.
- Run the architecture check and update generated architecture only if source changes require it.
- Use Grafana MCP/API to confirm dashboard, folder, links, datasources, and Home behavior after the MCP session is usable.
- After Flux applies the change, verify the live Grafana Home dashboard opens to Monitoring Radar.

Assumptions/defaults:

- Use Viewer-level Grafana MCP access for discovery and validation when possible.
- GitOps owns durable dashboard and Grafana configuration writes; live changes are temporary diagnostics only.
- Prefer the Home dashboard path over relying on a folderless Operator dashboard.
- Do not change alert rules as part of this dashboard-only implementation.
