# Implementation Plan: immich-app

**Branch**: `codex/immich-app` | **Date**: 2026-07-04 | **Spec**:
`specs/immich-app/spec.md`

**Input**: Feature specification from `specs/immich-app/spec.md`

## Summary

Add local-path storage and CloudNativePG as shared infrastructure, then deploy
Immich with NAS-backed media storage, CloudNativePG PostgreSQL, Authentik/OIDC,
Gateway API routing, Grafana dashboards, Homepage navigation, and synthetic
smoke coverage.

## Technical Context

**Risk Tier**: high
**Workflow Tier**: high
**Primary Areas**: Kubernetes, Terraform/Talos storage, Flux, SOPS secrets,
Gateway API, Authentik, Grafana, Homepage, synthetic smoke, generated docs
**Dependencies**: Flux, kubectl/kustomize, sops/age, terraform, npm synthetic
tests, architecture renderer, development branch verifier
**Storage**: Immich media uses `nfs-csi-media-storage`; database uses new
`local-path`; default NFS class remains unchanged
**Ingress**: Gateway API `HTTPRoute` only, `gateway/internal` and
`gateway/external`
**Secrets**: SOPS-encrypted `secret.yaml` manifests only
**Smoke Strategy**: development base reconcile plus manual Immich branch smoke
where feasible; production synthetic route smoke for post-merge route check
**Fanout Targets**: read-only/render validation, dashboard query review,
synthetic smoke test run, docs/evidence audit; no parallel tracked edits to the
same files
**Development Validation**: `--include-cluster-base` required for local-path and
CNPG; app smoke may document Authentik gap because development omits Authentik
**Post-Implementation SDD Conformance**: local SDD artifact audit only

## Constitution Check

*GATE: Must pass before tracked edits and be re-checked before commit.*

- [x] GitOps source of truth preserved; no durable live-cluster-only state.
- [x] No production-first mutation; development validation plan or exception is
      recorded for covered changes.
- [x] Gateway API invariant preserved; no new Kubernetes `Ingress` resources.
- [x] SOPS invariant preserved; no plaintext secret manifests staged.
- [x] NFS default considered for PVC-backed workloads.
- [x] Talos boundary preserved; no SSH-based node operations introduced.
- [x] Branch is `codex/immich-app`; worktree fallback path is recorded.
- [x] Documentation impact identified; docs and generated architecture updated.
- [x] PR review/status checks are the review gate.

## Project Structure

### SDD Artifacts

```text
specs/immich-app/
├── spec.md
├── plan.md
├── tasks.md
└── evidence.md
```

### Source Or Documentation Changes

```text
docs/architecture.md
docs/runbooks/immich.md
terraform/modules/vm/
terraform/modules/talos-bootstrap/
terraform/development/
terraform/production/
kubernetes/infra/controllers/local-path-provisioner/
kubernetes/infra/controllers/cloudnative-pg/
kubernetes/clusters/*/infra/
kubernetes/apps/immich/
kubernetes/clusters/production/apps/
kubernetes/infra/authentik/
kubernetes/infra/monitoring/grafana/
kubernetes/apps/homepage/
kubernetes/apps/synthetics/smoke/
tools/development/smoke-profiles/
specs/immich-app/
```

## Tiered TDD And Validation Plan

**TDD expectation**: No pre-existing failing app test seam exists. Use
render-first implementation, focused smoke tests, and development reconciliation
as the high-risk substitute.

**Local checks**:

- `sops -d kubernetes/apps/immich/secret.yaml >/dev/null`
- `sops -d kubernetes/infra/authentik/secret.yaml >/dev/null`
- `kubectl kustomize kubernetes/clusters/production`
- `kubectl kustomize kubernetes/clusters/development`
- `terraform -chdir=terraform/development validate`
- `terraform -chdir=terraform/production validate`
- `npm --prefix kubernetes/apps/synthetics/smoke test`
- `python3 tools/architecture/render.py --check`

**Development smoke**: Run development base validation with
`--include-cluster-base` if credentials are available; then run manual Immich
checks or document the missing Authentik/full-monitoring gap.

**Automated smoke preference**: Production synthetic route smoke should check
the exact `https://immich.${cluster_domain}` user path and treat Authentik/OAuth
entry as success.

**Completion evidence**: Record rendered intent locally in this PR and, after
merge, record Flux fetched SHA, applied Kustomizations/HelmReleases, live route,
dashboard data, and exact URL result.

**Fanout plan**: Mark independent validation/docs tasks with `[P]` in
`tasks.md`; consolidate all helper-lane results into `evidence.md`.

**Evidence destination**: `specs/immich-app/evidence.md`.

## Documentation Impact

Add `docs/runbooks/immich.md` and refresh `docs/architecture.md`.

## Implementation Steps

1. Bootstrap SDD artifacts.
2. Add local-path and CloudNativePG infrastructure.
3. Add Immich app, CNPG cluster, PVCs, route, secrets, and Flux wiring.
4. Add Authentik blueprint and encrypted client secret.
5. Add Grafana dashboard, Homepage tile, synthetic smoke entry, and docs.
6. Run local checks and development validation or record precise exception.
7. Update evidence and commit.

## Risks

| Risk | Mitigation |
| ---- | ---------- |
| Local storage is node-bound and not replicated | Document recovery model, keep Immich DB backups in NAS library backups, and make local-path non-default |
| OIDC-only login can lock out admins if Authentik is wrong | Validate blueprint/config and record production OIDC verification before declaring deployed |
| Chart/extension version mismatch | Pin chart, app image, and VectorChord image; record upgrade notes |
| Development cannot fully represent Authentik/Grafana | Run base/app checks and record exact unavailable layers |

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
| --------- | ---------- | ------------------------------------ |
| N/A | N/A | N/A |
