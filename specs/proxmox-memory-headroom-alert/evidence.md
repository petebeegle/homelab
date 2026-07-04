# Evidence: proxmox-memory-headroom-alert

**Branch**: `codex/proxmox-memory-headroom-alert`
**Risk Tier**: medium
**Started**: 2026-07-03T21:32:21Z
**Owner**: implementation-agent-proxmox-memory-headroom-alert

## Spec Kit Initialization

- Command: Not run; repository already contains `.specify/` scaffolding with
  Codex integration.
- Outcome: Reused existing Spec Kit scaffolding.
- Spec Kit version: Not changed by this implementation.
- Integration: Existing `.specify/integration.json` / Codex integration.
- Fallback: None.

## Workflow Validation

| Command | Result | Notes |
| ------- | ------ | ----- |
| `.specify/scripts/bash/check-prerequisites.sh --json --require-tasks --include-tasks` | PASS | Returned `FEATURE_DIR=/workspaces/homelab-ideas/proxmox-memory-headroom-alert/specs/proxmox-memory-headroom-alert` and `AVAILABLE_DOCS=["tasks.md"]`. |
| `python3 tools/codex-harness/validate_active_implementation.py --marker .codex/tmp/active-implementation --root "$(pwd)" --branch "$(git branch --show-current)"` | PASS | Completed before tracked edits. |
| `python3 tools/codex-harness/validate_implementation_plan.py --plan .codex/tmp/implementation-plan.yaml --marker .codex/tmp/active-implementation --root "$(pwd)" --branch "$(git branch --show-current)"` | PASS | Completed before tracked edits. |
| `python3 tools/codex-harness/validate_workflow_attestations.py --kind owner --attestation .codex/tmp/implementation-owner-attestation.yaml --marker .codex/tmp/active-implementation --plan .codex/tmp/implementation-plan.yaml --root "$(pwd)" --branch "$(git branch --show-current)"` | PASS | Completed before tracked edits. |
| `python3 tools/codex-harness/validate_sdd_context.py --marker .codex/tmp/active-implementation --root "$(pwd)" --branch "$(git branch --show-current)" --require-plan-artifacts` | PASS | Confirmed non-empty spec, plan, and tasks artifacts. |
| `python3 tools/codex-harness/validate_sdd_context.py --marker .codex/tmp/active-implementation --root "$(pwd)" --branch "$(git branch --show-current)" --require-plan-artifacts --require-evidence --head "$(git rev-parse HEAD)"` | PASS | Confirmed evidence artifact before commit. |

## Local Checks

| Command | Result | Notes |
| ------- | ------ | ----- |
| `pre-commit run yamllint --files kubernetes/infra/monitoring/grafana/alerting/alert-rules-proxmox.yaml` | PASS | `yamllint...Passed`. |
| `pre-commit run k8svalidate --files kubernetes/infra/monitoring/grafana/alerting/alert-rules-proxmox.yaml` | PASS | `k8svalidate...Passed`. |
| `kubectl kustomize kubernetes/infra/monitoring/grafana/alerting >/tmp/proxmox-alerting-render.yaml` | PASS | Rendered alerting kustomization to `/tmp/proxmox-alerting-render.yaml`. |
| Rendered rule inspection | PASS | Render includes UID `proxmox-host-memory-high`, title `Proxmox Host Memory Headroom Low`, the free-GiB expression, and threshold evaluator `lt` with parameter `3`. |

## Production Mimir Read-Only Query Validation

| Query | Observed Value | Notes |
| ----- | -------------- | ----- |
| `(proxmox_proxmox_node_memory_memtotal_bytes{proxmox_node="pve01"} - proxmox_proxmox_node_memory_memused_bytes{proxmox_node="pve01"}) / 1024 / 1024 / 1024` | `3.7434959411621094` GiB | Queried read-only through `KUBECONFIG=/home/vscode/.kube/homelab-production.config kubectl -n mimir port-forward svc/mimir-nginx 18080:80` and `curl -fsS -G --data-urlencode ... http://127.0.0.1:18080/prometheus/api/v1/query`. Response timestamp: `1783116527.814`. |
| `min((proxmox_proxmox_node_memory_memtotal_bytes - proxmox_proxmox_node_memory_memused_bytes) / 1024 / 1024 / 1024)` | `3.7434959411621094` GiB | Same read-only port-forward and Prometheus query API. Response timestamp: `1783116527.802`. |

## Development Validation

- Profile: none
- Branch slug: N/A
- HEAD: Current validation ran before final commit; exact commit SHA is recorded
  in `.codex/tmp/pr-summary.md` and final handoff after commit creation.
- Report path: N/A
- Cleanup: N/A
- Result or exception: Development branch verifier is not suitable for this
  monitoring/Grafana alerting change because the relevant behavior depends on
  production Proxmox metrics and Grafana/Mimir alert semantics. Substitute checks
  are focused local render/schema validation plus read-only production Mimir
  query validation.

## Documentation Impact

- Updated: Alert title, summary, description, and runbook annotation in
  `kubernetes/infra/monitoring/grafana/alerting/alert-rules-proxmox.yaml`.
- Generated docs: Not expected; no Kubernetes topology, Terraform source, or
  architecture source changes that affect `docs/architecture.md`.
- No-docs rationale: No separate runbook or ADR change needed; operator-facing
  alert annotations are the documentation surface for this fix.

## Exceptions And Follow-Ups

- TDD exception: declarative alert-rule correction with no practical failing
  unit-test seam; substitute focused render/schema validation and live read-only
  query checks.
- Development validation exception: development branch verifier is not suitable
  for monitoring/Grafana alerting semantics for production Proxmox metrics.
- Post-merge follow-up: verify production Grafana ruler/CR state after Flux
  reconciles the merged desired state; do not mutate production from this branch.

## Final State

- Final branch: `codex/proxmox-memory-headroom-alert`
- Final HEAD: Created after committed evidence; exact SHA recorded in
  `.codex/tmp/pr-summary.md` and final handoff.
- Commit: Conventional commit created after validation evidence was recorded.
- Verifier approval: not created by implementation owner
