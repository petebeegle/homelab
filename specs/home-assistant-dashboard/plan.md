# Implementation Plan: home-assistant-dashboard

**Branch**: `codex/home-assistant-dashboard` | **Date**: 2026-07-03 | **Spec**:
`specs/home-assistant-dashboard/spec.md`

**Input**: Feature specification from `specs/home-assistant-dashboard/spec.md`

## Summary

Add a Home Assistant dashboard through the existing Grafana Operator pattern. The dashboard uses only live-smoked existing Mimir and Loki queries for health, routing, resource, event/log, integration-activity, and synthetic smoke panels.

## Technical Context

**Risk Tier**: medium
**Workflow Tier**: medium
**Primary Areas**: Kubernetes, Grafana, observability, SDD
**Dependencies**: kubectl, jq, production kubeconfig for read-only query smoke
**Storage**: N/A
**Ingress**: N/A; no new Gateway routes or Ingress resources
**Secrets**: No new secrets
**Development Validation**: none; this dashboard is validated by local render checks plus production read-only query smoke because development lacks the production observability data needed for strict non-empty Home Assistant panels

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
specs/home-assistant-dashboard/
├── spec.md
├── plan.md
├── tasks.md
└── evidence.md
```

### Source Or Documentation Changes

```text
kubernetes/infra/monitoring/grafana/folders.yaml
kubernetes/infra/monitoring/grafana/dashboards/kustomization.yaml
kubernetes/infra/monitoring/grafana/dashboards/home-assistant-dashboard.yaml
kubernetes/infra/monitoring/grafana/dashboards/home-assistant-dashboard.json
specs/home-assistant-dashboard/
```

## Tiered TDD And Validation Plan

**TDD expectation**: No executable code test seam is introduced. The failing condition would be an empty query, invalid dashboard JSON, or failed kustomize render.

**Local checks**:

- `jq empty kubernetes/infra/monitoring/grafana/dashboards/home-assistant-dashboard.json`
- `kubectl kustomize kubernetes/infra/monitoring/grafana/dashboards`
- `python3 tools/architecture/render.py --check`
- `python3 tools/codex-harness/validate_sdd_context.py --marker .codex/tmp/active-implementation --root "$(pwd)" --branch "$(git branch --show-current)" --require-plan-artifacts`

**Development smoke**: none; production read-only query smoke is required because development does not carry the Home Assistant production observability history.

**Evidence destination**: `specs/home-assistant-dashboard/evidence.md` and `.codex/tmp/pr-summary.md`.

## Documentation Impact

SDD artifacts record the dashboard behavior and evidence. `docs/architecture.md` is checked and updated only if generated inventory changes.

## Implementation Steps

1. Validate workflow runtime files before tracked edits.
2. Run strict non-empty query smoke against production Mimir and Loki.
3. Add SDD artifacts.
4. Add Home Assistant Grafana folder, dashboard CR, dashboard JSON, and kustomization entries.
5. Run JSON, kustomize, generated architecture, and SDD context checks.
6. Record final evidence and commit.

## Risks

| Risk | Mitigation |
| ---- | ---------- |
| Loki label shape changes could empty log panels. | Smoke every included query before implementation and record results. |
| Dashboard implies authoritative integration inventory. | Title the panel as observed integration activity from logs only. |
| Development cluster lacks equivalent observability history. | Use read-only production query smoke and local render validation. |

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
| --------- | ---------- | ------------------------------------ |
| N/A | N/A | N/A |
