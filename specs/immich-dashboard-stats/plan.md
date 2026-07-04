# Implementation Plan: immich-dashboard-stats

**Branch**: `codex/immich-dashboard-stats` | **Date**: 2026-07-04 |
**Spec**: `specs/immich-dashboard-stats/spec.md`

**Input**: Feature specification from
`specs/immich-dashboard-stats/spec.md`

## Summary

Add a dedicated annotated Immich microservices metrics Service for Alloy's
existing service-annotation scraper, then replace the Immich Grafana dashboard
with user-oriented upload, queue, job, processing, storage, resource, and log
panels. Keep API metrics scraping unchanged and avoid global Alloy changes.

## Technical Context

**Risk Tier**: medium
**Workflow Tier**: medium
**Primary Areas**: Kubernetes, Flux, Grafana, observability, SDD
**Dependencies**: kubectl, flux CLI, jq, production kubeconfig for read-only
query smoke
**Storage**: N/A; no PVC changes
**Ingress**: N/A; no Gateway API route changes
**Secrets**: N/A; no secret changes
**Smoke Strategy**: production read-only Mimir/Loki query smoke plus local
render checks; post-merge live scrape verification recorded if unreconciled
**Fanout Targets**: query smoke, render validation, evidence updates
**Development Validation**: none; dashboard data depends on production Immich
observability, with substitute query smoke and render checks
**Post-Implementation SDD Conformance**: local workflow docs only

## Constitution Check

*GATE: Must pass before tracked edits and be re-checked before commit.*

- [x] GitOps source of truth preserved; no durable live-cluster-only state.
- [x] No production-first mutation; development validation exception and
      substitute query smoke are recorded.
- [x] Gateway API invariant preserved; no new Kubernetes `Ingress` resources.
- [x] SOPS invariant preserved; no plaintext secret manifests staged.
- [x] NFS default considered for PVC-backed workloads; no PVC changes.
- [x] Talos boundary preserved; no SSH-based node operations introduced.
- [x] Branch is `codex/immich-dashboard-stats`; worktree fallback is recorded.
- [x] Documentation impact identified; generated architecture will be checked.
- [x] PR review/status checks are the review gate.

## Project Structure

### SDD Artifacts

```text
specs/immich-dashboard-stats/
├── spec.md
├── plan.md
├── tasks.md
└── evidence.md
```

### Source Or Documentation Changes

```text
kubernetes/apps/immich/base/metrics-service.yaml
kubernetes/apps/immich/base/kustomization.yaml
kubernetes/infra/monitoring/grafana/dashboards/immich-dashboard.json
docs/architecture.md
specs/immich-dashboard-stats/
```

## Tiered TDD And Validation Plan

**TDD expectation**: No executable code seam is introduced. The failing
condition is invalid JSON, missing rendered Service, missing rendered dashboard,
or dashboard queries that return no usable live data.

**Local checks**:

- `jq empty kubernetes/infra/monitoring/grafana/dashboards/immich-dashboard.json`
- `kubectl kustomize kubernetes/apps/immich`
- `branch_slug=immich-dashboard-stats cluster_domain=dev.lab.petebeegle.com kubectl kustomize kubernetes/apps/immich/branch | flux envsubst --strict`
- `kubectl kustomize kubernetes/infra/monitoring/grafana/dashboards`
- `kubectl kustomize kubernetes/infra/monitoring/grafana`
- `python3 tools/architecture/render.py --check`
- `python3 tools/codex-harness/validate_sdd_context.py --root "$(pwd)" --branch "$(git branch --show-current)" --require-plan-artifacts`

**Development smoke**: none; development does not carry the production Immich
upload/processing metric history needed for strict dashboard smoke. Substitute
checks are production read-only query smoke and deterministic local render
validation.

**Automated smoke preference**: For user-facing, routed, deployed, or
operational changes, prefer automated smoke in this order: development branch
profile; production synthetic smoke or one-off in-cluster Job; scriptable
Gateway/DNS/browser smoke against the exact user URL; manual browser checks
only as supplemental evidence.

## Implementation Notes

1. Create `immich-server-metrics-ms` as a small standalone Service rather than
   changing Alloy's global discovery or relying on ServiceMonitor discovery.
2. Query `immich_queues_*_active` and `immich_jobs_*_(success|failed|skipped)_total`
   only after the microservices metrics scrape target exists.
3. Use `OR on() vector(0)` fallbacks where a successful zero is useful, while
   keeping labels for grouped panels where data exists.

## Risks

| Risk | Mitigation |
| ---- | ---------- |
| New `8082` target cannot be verified before merge because Flux has not reconciled the branch. | Record post-merge verification and validate the rendered service locally. |
| Dashboard panels become empty if a metric family is absent after an Immich upgrade. | Use query-smoked current metric families and conservative fallback vectors for stat panels. |
| Generated architecture inventory changes. | Run `render.py --check`, then `--write` if required. |
