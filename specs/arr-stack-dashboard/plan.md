# Implementation Plan: arr-stack-dashboard

**Branch**: `codex/arr-stack-dashboard` | **Date**: 2026-07-03 | **Spec**:
`specs/arr-stack-dashboard/spec.md`

**Input**: Feature specification from `specs/arr-stack-dashboard/spec.md`

## Summary

Add an arr stack dashboard through the existing Grafana Operator pattern. The dashboard uses only live-smoked existing Mimir and Loki query families for health, routing, storage, resources, logs, and download/import activity.

## Technical Context

**Risk Tier**: medium
**Workflow Tier**: medium
**Primary Areas**: Kubernetes, Grafana, observability, SDD
**Dependencies**: kubectl, jq, production kubeconfig for read-only query smoke
**Storage**: N/A
**Ingress**: N/A; no new Gateway routes or Ingress resources
**Secrets**: No new secrets
**Development Validation**: none; this dashboard is validated by local render checks plus production read-only query smoke because development lacks the private arr stack observability history needed for strict non-empty panels

## Constitution Check

*GATE: Must pass before tracked edits and be re-checked before commit.*

- [x] GitOps source of truth preserved; no durable live-cluster-only state.
- [x] No production-first mutation; read-only production query smoke recorded with local render substitute.
- [x] Gateway API invariant preserved; no new Kubernetes `Ingress` resources.
- [x] SOPS invariant preserved; no plaintext secret manifests staged.
- [x] NFS default considered for PVC-backed workloads.
- [x] Talos boundary preserved; no SSH-based node operations introduced.
- [x] Sibling clone ownership files validated before tracked edits.
- [x] Documentation impact identified; SDD artifacts record the dashboard scope and generated architecture is checked.
- [x] Separate verifier approval required before PR creation.

## Project Structure

### SDD Artifacts

```text
specs/arr-stack-dashboard/
├── spec.md
├── plan.md
├── tasks.md
└── evidence.md
```

### Source Or Documentation Changes

```text
kubernetes/infra/monitoring/grafana/folders.yaml
kubernetes/infra/monitoring/grafana/dashboards/kustomization.yaml
kubernetes/infra/monitoring/grafana/dashboards/arr-stack-dashboard.yaml
kubernetes/infra/monitoring/grafana/dashboards/arr-stack-dashboard.json
specs/arr-stack-dashboard/
```

## Tiered TDD And Validation Plan

**TDD expectation**: No executable code test seam is introduced. The failing condition would be an empty query family, invalid dashboard JSON, or failed kustomize render.

**Local checks**:

- `jq empty kubernetes/infra/monitoring/grafana/dashboards/arr-stack-dashboard.json`
- `kubectl kustomize kubernetes/infra/monitoring/grafana/dashboards`
- `kubectl kustomize kubernetes/infra/monitoring/grafana`
- `python3 tools/architecture/render.py --check`
- `python3 tools/codex-harness/validate_sdd_context.py --marker .codex/tmp/active-implementation --root "$(pwd)" --branch "$(git branch --show-current)" --require-plan-artifacts`

**Development smoke**: none; production read-only query smoke is required because development does not carry private arr stack observability history.

**Evidence destination**: `specs/arr-stack-dashboard/evidence.md` and `.codex/tmp/pr-summary.md`.

## Documentation Impact

SDD artifacts record the dashboard behavior and evidence. `docs/architecture.md` is checked and updated only if generated inventory changes.

## Implementation Steps

1. Validate workflow runtime files before tracked edits.
2. Run strict non-empty query smoke against production Mimir and Loki.
3. Add SDD artifacts.
4. Add arr stack Grafana folder, dashboard CR, dashboard JSON, and kustomization entries.
5. Run JSON, kustomize, generated architecture, and SDD context checks.
6. Record final evidence and commit.

## Risks

| Risk | Mitigation |
| ---- | ---------- |
| Private namespace set changes. | Keep the regex explicit in SDD evidence and dashboard queries. |
| Loki label shape changes could empty log panels. | Smoke the included log query families before implementation and record results. |
| Dashboard implies API-level queue health. | Use titles that frame panels as logs and Kubernetes observations only. |

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
| --------- | ---------- | ------------------------------------ |
| N/A | N/A | N/A |
