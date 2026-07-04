# Implementation Plan: immich-dashboard-inline

**Branch**: `codex/immich-dashboard-inline` | **Date**: 2026-07-04 |
**Spec**: `specs/immich-dashboard-inline/spec.md`

**Input**: Feature specification from `specs/immich-dashboard-inline/spec.md`

## Summary

Convert the Immich Grafana dashboard from ConfigMap-backed content to inline
`GrafanaDashboard.spec.json`. This makes dashboard content part of the CR spec,
forcing a Grafana Operator reconcile/import when dashboard JSON changes.

## Technical Context

**Risk Tier**: medium
**Workflow Tier**: medium
**Primary Areas**: Grafana, Kubernetes, Flux, SDD
**Dependencies**: kubectl, jq, python3
**Storage**: N/A
**Ingress**: N/A
**Secrets**: N/A
**Smoke Strategy**: local render checks plus post-merge Grafana API verification
**Fanout Targets**: N/A
**Development Validation**: none; this corrects production Grafana operator
import behavior and is validated by render plus production API after merge
**Post-Implementation SDD Conformance**: local workflow docs only

## Constitution Check

- [x] GitOps source of truth preserved; no durable live-cluster-only state.
- [x] No production-first mutation; live checks were read-only.
- [x] Gateway API invariant preserved; no route changes.
- [x] SOPS invariant preserved; no secret changes.
- [x] NFS default considered; no PVC changes.
- [x] Talos boundary preserved; no SSH operations.
- [x] Branch is `codex/immich-dashboard-inline`.
- [x] Documentation impact identified; generated architecture will be checked.
- [x] PR review/status checks are the review gate.

## Project Structure

```text
specs/immich-dashboard-inline/
├── spec.md
├── plan.md
├── tasks.md
└── evidence.md
```

Expected source changes:

```text
kubernetes/infra/monitoring/grafana/dashboards/immich-dashboard.yaml
kubernetes/infra/monitoring/grafana/dashboards/kustomization.yaml
kubernetes/infra/monitoring/grafana/dashboards/immich-dashboard.json
docs/architecture.md
```

## Validation Plan

- `kubectl kustomize kubernetes/infra/monitoring/grafana/dashboards`
- `kubectl kustomize kubernetes/infra/monitoring/grafana`
- Extract inline dashboard JSON from the rendered `GrafanaDashboard` and parse
  it with `jq`.
- `python3 tools/architecture/render.py --check`
- `python3 tools/codex-harness/validate_sdd_context.py --root "$(pwd)" --branch "$(git branch --show-current)" --require-plan-artifacts`

Post-merge: query Grafana API for `uid=immich-overview` and confirm new panel
titles such as `Active Background Queues` and `Job Success / Min`.
