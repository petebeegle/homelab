# Implementation Plan: Jellyfin Migration Envsubst

**Branch**: `codex/jellyfin-migration-envsubst` | **Date**: 2026-08-08 | **Spec**:
`specs/jellyfin-migration-envsubst/spec.md`

**Input**: Feature specification from
`specs/jellyfin-migration-envsubst/spec.md`

## Summary

Repair the merged Jellyfin migration's Flux build failure by annotating only
the generated migration ConfigMap to opt it out of post-build variable
substitution. Keep substitution active for the application values ConfigMap,
and add regression coverage that renders the manifests through strict Flux
substitution, verifies the script is preserved, and executes that rendered
script through the existing migration safety cases.

## Technical Context

**Risk Tier**: medium
**Workflow Tier**: medium
**Primary Areas**: Kubernetes, Flux, shell migration, Python tests
**Dependencies**: Spec Kit, Flux CLI, kubectl, Python standard library
**Storage**: Existing `local-path` target and retained read-only
`jellyfin-config-v2` NFS source; no storage change
**Ingress**: Existing Gateway API `HTTPRoute`; no route change
**Secrets**: Existing SOPS-encrypted secret references; no secret change
**Smoke Strategy**: Exact local `flux build kustomization
--strict-substitute` regression, focused migration tests, production
Flux/workload/storage inspection, and exact HTTPS web plus SSO-start probes
**Fanout Targets**: GitHub/Flux revision state, Kubernetes rollout/storage state,
and user-path/observability checks are independent read-only lanes
**Development Validation**: Exact local render/substitution and unit execution.
The routed Jellyfin development profile cannot schedule because its pinned GPU
resource is absent; the user explicitly accepted that known limitation for this
work.
**Post-Implementation SDD Conformance**: Local artifacts only; no template or
upstream Spec Kit change

## Human Gates

**Spec Gate**: Approved by the user's instruction to verify the merged rollout
and iterate as needed.

**Checklist Status**: PASS, 15/15 items in
`specs/jellyfin-migration-envsubst/checklists/requirements.md`.

**Plan Gate**: Approved by the user's instruction to iterate on verification
failures; the change is constrained to the exact diagnosed blocker.

**Expected Task/Analyze Gate**: Tasks plus analyze required before
implementation.

## Constitution Check

*GATE: Must pass before tracked edits and be re-checked before commit.*

- [x] GitOps source of truth preserved; no durable live-cluster-only state.
- [x] No production-first mutation; development validation plan or exception is
      recorded for covered changes.
- [x] Gateway API invariant preserved; no new Kubernetes `Ingress` resources.
- [x] SOPS invariant preserved; no plaintext secret manifests staged.
- [x] NFS default considered for PVC-backed workloads; the approved local-config
      decision remains binding and the NFS rollback source is retained.
- [x] Talos boundary preserved; no SSH-based node operations introduced.
- [x] Branch is `codex/jellyfin-migration-envsubst`; isolated worktree
      `/home/vscode/homelab-worktrees/jellyfin-migration-envsubst` is
      intentional and recorded when relevant.
- [x] Documentation impact identified; docs updated or no-docs rationale
      recorded.
- [x] PR review/status checks are the review gate.

## Project Structure

### SDD Artifacts

```text
specs/jellyfin-migration-envsubst/
├── checklists/requirements.md
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── contracts/migration-configmap.md
├── quickstart.md
├── tasks.md
└── evidence.md
```

### Source Or Documentation Changes

```text
kubernetes/apps/jellyfin/kustomization.yaml
tools/development/tests/test_jellyfin_config_migration.py
.github/workflows/ci.yml
specs/jellyfin-migration-envsubst/**
```

## Tiered TDD And Validation Plan

**TDD expectation**: First extend the focused test to render and execute the
post-substitution script. At the merged baseline, that test must fail with
Flux's `bad substitution`; after the ConfigMap annotation, it must pass without
changing migration behavior.

**Local checks**:

- `python3 -m unittest tools.development.tests.test_jellyfin_config_migration`
- `python3 tools/architecture/render.py --check`
- `pre-commit run --all-files`

**Development smoke**: The exact Flux post-build rendering path and migration
script execution are automated locally. Routed development workload smoke is an
explicit exception because the development node lacks the pinned GPU resource;
the user directed us not to resolve that infrastructure mismatch now.

**Automated smoke preference**: For user-facing, routed, deployed, or
operational changes, prefer automated smoke in this order: development branch
profile; production synthetic smoke or one-off in-cluster Job; scriptable
Gateway/DNS/browser smoke against the exact user URL; manual browser checks only
as supplemental evidence.

**Completion evidence**: For deploy follow-up, record source fetched SHA, target
kustomization or HelmRelease applied SHA, live resource spec, Gateway/listener
match when applicable, and exact user-facing URL result.

**Fanout plan**: One lane verifies GitHub merge and Flux source/application
revisions, one verifies Kubernetes deployment/PVC/init state, and one verifies
web/SSO paths plus logs. The main lane owns all tracked edits and consolidates
timestamps, SHAs, commands, and outcomes into `evidence.md`.

**Evidence destination**: `specs/jellyfin-migration-envsubst/evidence.md`.

## Documentation Impact

No canonical runbook, ADR, generated architecture, or agent guidance change is
required. The binding Jellyfin local-storage decision remains unchanged; this
implementation corrects only Flux processing of the migration payload. SDD
artifacts record the failure, exception, repair, and verification evidence.

## Implementation Steps

1. Add a failing regression that performs a strict local Flux Kustomization
   build, extracts the generated ConfigMap script, confirms
   it matches the source, and runs the existing migration cases against it.
2. Annotate only `jellyfin-config-migration` with
   `kustomize.toolkit.fluxcd.io/substitute: disabled`.
3. Run focused tests, strict production render, architecture check, and
   repository validation; then push a PR and require GitHub status checks.
4. After merge, verify fetched/applied revisions, the live deployment and PVCs,
   migration init state/logs, and exact web and SSO-start paths.
5. If all acceptance evidence passes, leave cleanup as a separately reviewed
   follow-up; do not remove rollback assets in this repair.

## Risks

| Risk | Mitigation |
| ---- | ---------- |
| Flux CLI behavior differs from kustomize-controller | Use the documented resource annotation and verify the merged revision in the controller. |
| Annotation disables desired app substitutions | Scope it only to the migration ConfigMap and assert the values ConfigMap still substitutes. |
| Tests execute repository source instead of controller output | Extract and execute the script from the post-substitution rendered ConfigMap. |
| Migration changes authentication or storage semantics | Leave the script and workload manifests unchanged and rerun all fail-closed cases plus live invariants. |
| Production outage during `Recreate` migration | Confirm the old deployment remains live until a buildable revision exists, then verify init completion and user paths immediately after rollout. |

## Complexity Tracking

> Fill only when the constitution check has a violation that must be justified.

| Violation | Why Needed | Simpler Alternative Rejected Because |
| --------- | ---------- | ------------------------------------ |
| N/A | N/A | N/A |
