# Implementation Plan: fix-immich-cnpg-scrape

**Branch**: `codex/fix-immich-cnpg-scrape` | **Date**: 2026-07-04 | **Spec**:
`specs/fix-immich-cnpg-scrape/spec.md`

**Input**: Feature specification from
`specs/fix-immich-cnpg-scrape/spec.md`

## Summary

Add an Alloy service discovery relabel drop for CloudNativePG-generated
Services so inherited `9187` annotations do not create unreachable service
scrape targets. Keep the existing PostgreSQL pod metrics annotations and rely on
Alloy pod discovery for database metrics.

## Technical Context

**Risk Tier**: high
**Workflow Tier**: high
**Primary Areas**: Kubernetes, Flux, observability, shared Alloy config
**Dependencies**: kubectl, helm, curl, jq
**Storage**: Existing Immich PostgreSQL PVC unchanged
**Ingress**: N/A
**Secrets**: No secret changes
**Smoke Strategy**: live read-only production metrics query plus local Alloy and
production render checks; no user-facing route change
**Fanout Targets**: N/A
**Development Validation**: none with exception; development does not run the
production monitoring stack by default and the active target set is
production-specific
**Post-Implementation SDD Conformance**: local runbooks only

## Constitution Check

*GATE: Must pass before tracked edits and be re-checked before commit.*

- [x] GitOps source of truth preserved; no durable live-cluster-only state.
- [x] No production-first mutation; development validation plan or exception is
      recorded for covered changes.
- [x] Gateway API invariant preserved; no new Kubernetes `Ingress` resources.
- [x] SOPS invariant preserved; no plaintext secret manifests staged.
- [x] NFS default considered for PVC-backed workloads.
- [x] Talos boundary preserved; no SSH-based node operations introduced.
- [x] Branch is `codex/fix-immich-cnpg-scrape`; fallback sibling worktree mode
      is intentional because `/workspaces/homelab-worktrees` is not writable.
- [x] Documentation impact identified; no docs update required for this narrow
      app manifest correction.
- [x] PR review/status checks are the review gate.

## Project Structure

### SDD Artifacts

```text
specs/fix-immich-cnpg-scrape/
├── spec.md
├── plan.md
├── tasks.md
└── evidence.md
```

### Source Or Documentation Changes

```text
kubernetes/infra/monitoring/alloy/config/config.alloy
specs/fix-immich-cnpg-scrape/
```

## Tiered TDD And Validation Plan

**TDD expectation**: No executable code test seam. Use focused manifest render
checks and live read-only production evidence.

**Local checks**:

- `kubectl kustomize kubernetes/infra/monitoring/alloy`
- `helm template immich oci://ghcr.io/immich-app/immich-charts/immich --version 0.13.1 --namespace immich -f kubernetes/apps/immich/base/values.yaml`
- `kubectl kustomize kubernetes/clusters/production`

**Development smoke**: none with exception; development does not run the
production Immich/CNPG monitoring target set by default.

**Automated smoke preference**: No user-facing route behavior changes. Use live
metrics query against production Mimir as the operational smoke signal.

**Completion evidence**: Record live target query, render outcomes, final branch
state, and deployment follow-up needed after PR merge.

**Fanout plan**: N/A.

**Evidence destination**:
`specs/fix-immich-cnpg-scrape/evidence.md`.

## Documentation Impact

No runbook or architecture change required. The generated architecture maps
component activation and is not affected by this app manifest metadata change.

## Implementation Steps

1. Add a CloudNativePG service drop rule to Alloy service discovery.
2. Render Alloy and production manifests to confirm valid desired state.
3. Record live read-only query evidence and validation outcomes.

## Risks

| Risk | Mitigation |
| ---- | ---------- |
| PostgreSQL metrics disappear | Live evidence shows pod discovery already scrapes the PostgreSQL pod successfully; only service annotations are removed. |
| Alert remains until Flux applies the change | Record post-merge verification steps for Flux reconciliation and Mimir query. |

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
| --------- | ---------- | ------------------------------------ |
| N/A | N/A | N/A |
