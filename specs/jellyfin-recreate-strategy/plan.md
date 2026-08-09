# Implementation Plan: Jellyfin Recreate Strategy

**Branch**: `codex/jellyfin-recreate-strategy` | **Date**: 2026-08-09 | **Spec**:
`specs/jellyfin-recreate-strategy/spec.md`

**Input**: Feature specification from
`specs/jellyfin-recreate-strategy/spec.md`

## Summary

Make the Helm-rendered Deployment explicitly clear `strategy.rollingUpdate`
when selecting `Recreate`, so Helm controller server-side apply can transition
the existing live Deployment without producing an invalid merged object. Extend
the focused Jellyfin integration test to template chart 3.2.0 and assert both
the clear operation and unchanged migration invariants.

## Technical Context

**Risk Tier**: medium
**Workflow Tier**: medium
**Primary Areas**: Kubernetes, Helm, Flux, Python tests
**Dependencies**: Spec Kit, Helm, Flux CLI, kubectl, Python standard library
**Storage**: Existing local-path target and retained NFS rollback source; no
storage change
**Ingress**: Existing Gateway API routes; no route change
**Secrets**: Existing SOPS-encrypted references; no secret change
**Smoke Strategy**: Exact Helm template strategy assertion, focused migration
tests, production Flux/Helm/workload/storage verification, and exact HTTPS web
plus SSO-start probes
**Fanout Targets**: GitHub/Flux revision state, rollout/storage/init state, and
user-path/observability remain independent read-only lanes
**Development Validation**: Exact chart/render/test path. Routed development
smoke remains unavailable because the pinned GPU resource is absent, which the
user explicitly excluded from this work.
**Post-Implementation SDD Conformance**: Local artifacts only; no workflow or
template change. The agent context update script is absent in this repository.

## Human Gates

**Spec Gate**: Approved by the user's instruction to keep iterating on rollout
blockers.

**Checklist Status**: PASS, 16/16 items in
`specs/jellyfin-recreate-strategy/checklists/requirements.md`.

**Plan Gate**: Approved by the same instruction; the approach is the exact
rendered remediation proven by the read-only production lane.

**Expected Task/Analyze Gate**: Tasks plus analyze required before
implementation.

## Constitution Check

*GATE: Must pass before tracked edits and be re-checked before commit.*

- [x] GitOps source of truth preserved; no durable live-cluster-only state.
- [x] No production-first mutation; development validation plan or exception is
      recorded for covered changes.
- [x] Gateway API invariant preserved; no new Kubernetes `Ingress` resources.
- [x] SOPS invariant preserved; no plaintext secret manifests staged.
- [x] NFS default considered; the binding local-config exception and retained
      NFS rollback source remain unchanged.
- [x] Talos boundary preserved; no SSH-based node operations introduced.
- [x] Branch is `codex/jellyfin-recreate-strategy`; isolated worktree
      `/home/vscode/homelab-worktrees/jellyfin-recreate-strategy` is
      intentional and recorded when relevant.
- [x] Documentation impact identified; docs updated or no-docs rationale
      recorded.
- [x] PR review/status checks are the review gate.

## Project Structure

### SDD Artifacts

```text
specs/jellyfin-recreate-strategy/
├── checklists/requirements.md
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── contracts/deployment-strategy.md
├── quickstart.md
├── tasks.md
└── evidence.md
```

### Source Or Documentation Changes

```text
kubernetes/apps/jellyfin/values.yaml
tools/development/tests/test_jellyfin_config_migration.py
.github/workflows/ci.yml
.specify/feature.json
specs/jellyfin-recreate-strategy/**
```

## Tiered TDD And Validation Plan

**TDD expectation**: Add the chart strategy assertion before the values repair.
The merged baseline must fail because the chart omits the explicit clear; the
repair must pass with `rollingUpdate: null` and `type: Recreate` together.

**Local checks**:

- `python3 -m unittest tools.development.tests.test_jellyfin_config_migration`
- `helm template jellyfin jellyfin/jellyfin --version 3.2.0 -f kubernetes/apps/jellyfin/values.yaml`
- `python3 tools/architecture/render.py --check`
- `pre-commit run --all-files`

**Development smoke**: Exact Helm/chart rendering and migration tests substitute
for the routed development profile. The profile cannot schedule because the
development environment lacks the pinned GPU resource; the user directed us not
to change that infrastructure.

**Automated smoke preference**: For user-facing, routed, deployed, or
operational changes, prefer automated smoke in this order: development branch
profile; production synthetic smoke or one-off in-cluster Job; scriptable
Gateway/DNS/browser smoke against the exact user URL; manual browser checks only
as supplemental evidence.

**Completion evidence**: For deploy follow-up, record source fetched SHA, target
kustomization or HelmRelease applied SHA, live resource spec, Gateway/listener
match when applicable, and exact user-facing URL result.

**Fanout plan**: One read-only lane owns GitHub/Flux revision evidence, one owns
Helm/workload/PVC/init evidence, and one owns routes/user paths/observability.
The main lane owns tracked edits and consolidates all findings in `evidence.md`.

**Evidence destination**: `specs/jellyfin-recreate-strategy/evidence.md`.

## Documentation Impact

No canonical docs, ADR, generated architecture, or agent guidance change is
required. The binding migration design already requires Recreate; this repair
only makes the transition explicit for server-side apply.

## Implementation Steps

1. Extend the focused test to template the pinned chart and fail unless the
   Deployment strategy explicitly clears rolling-update while selecting
   Recreate.
2. Add `rollingUpdate: null` under the Jellyfin deployment strategy values.
3. Add Helm setup to the existing CI job that runs the focused test.
4. Run focused, architecture, SDD, and repository checks; publish a draft PR and
   require all checks before merge.
5. After merge, rerun the layered production acceptance. Keep all migration
   assets if any technical or binding authentication gate remains unverified.

## Risks

| Risk | Mitigation |
| ---- | ---------- |
| Null is dropped before apply | Assert the pinned chart output contains the explicit null. |
| Repair changes unrelated workload fields | Limit the values diff to one key and assert migration/storage invariants. |
| Helm rollback disrupts the old workload | Confirm rollback remains healthy and require green render/review gates before the next merge. |
| Technical success is mistaken for authentication acceptance | Record exact authenticated limitations and defer cleanup until binding gates pass. |

## Complexity Tracking

> Fill only when the constitution check has a violation that must be justified.

| Violation | Why Needed | Simpler Alternative Rejected Because |
| --------- | ---------- | ------------------------------------ |
| N/A | N/A | N/A |
