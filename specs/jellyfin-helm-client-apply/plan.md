# Implementation Plan: Jellyfin Helm Client Apply

**Branch**: `codex/jellyfin-helm-client-apply` | **Date**: 2026-08-09 | **Spec**:
`specs/jellyfin-helm-client-apply/spec.md`

**Input**: `specs/jellyfin-helm-client-apply/spec.md`

## Summary

Explicitly disable server-side apply for Jellyfin Helm upgrade and rollback.
This makes Helm use the strategic client-side path that a read-only full server
dry-run proved can remove the API-defaulted rolling strategy field. Do not force
replacement; keep the existing strategy intent and migration safeguards.

## Technical Context

**Risk Tier**: medium
**Workflow Tier**: medium
**Primary Areas**: Kubernetes, HelmRelease, Flux, Python tests
**Dependencies**: Spec Kit, Helm, Flux CLI, kubectl, Python
**Storage**: Existing local target and retained NFS rollback source; unchanged
**Ingress**: Existing Gateway API routes; unchanged
**Secrets**: Existing SOPS references; unchanged
**Smoke Strategy**: Full Flux render assertions, focused Helm/migration tests,
production controller/workload/storage verification, exact web/SSO paths
**Fanout Targets**: GitHub/Flux, rollout/storage/init, user paths/observability
**Development Validation**: Exact render and tests. Routed dev remains blocked
by the known missing pinned GPU resource, explicitly excluded by the user.
**Post-Implementation SDD Conformance**: Local artifacts only; agent context
update script is absent.

## Human Gates

**Spec Gate**: Approved by user direction to keep iterating.

**Checklist Status**: PASS, 12/12.

**Plan Gate**: Approved within the same direction; exact read-only full Helm
server dry-run proves the scoped approach.

**Expected Task/Analyze Gate**: Tasks plus analyze required.

## Constitution Check

*GATE: Must pass before tracked edits and be re-checked before commit.*

- [x] GitOps source of truth preserved; no durable live-cluster-only state.
- [x] No production-first mutation; development validation plan or exception is
      recorded for covered changes.
- [x] Gateway API invariant preserved; no new Kubernetes `Ingress` resources.
- [x] SOPS invariant preserved; no plaintext secret manifests staged.
- [x] NFS default and binding local-config exception preserved.
- [x] Talos boundary preserved; no SSH-based node operations introduced.
- [x] Branch/worktree contract is intentional at
      `/home/vscode/homelab-worktrees/jellyfin-helm-client-apply`.
      intentional and recorded when relevant.
- [x] Documentation impact identified; docs updated or no-docs rationale
      recorded.
- [x] PR review/status checks are the review gate.

## Project Structure

### SDD Artifacts

```text
specs/jellyfin-helm-client-apply/
├── checklists/requirements.md
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── contracts/helm-action-mode.md
├── quickstart.md
├── tasks.md
└── evidence.md
```

### Source Or Documentation Changes

```text
kubernetes/apps/jellyfin/app.yaml
tools/development/tests/test_jellyfin_config_migration.py
.specify/feature.json
specs/jellyfin-helm-client-apply/**
```

## Tiered TDD And Validation Plan

**TDD expectation**: Add render assertions for both action modes and absence of
force before editing the HelmRelease. Baseline must fail those mode assertions.

**Local checks**:

- `python3 -m unittest tools.development.tests.test_jellyfin_config_migration`
- `python3 tools/architecture/render.py --check`
- `pre-commit run --all-files`

**Development smoke**: Exact render/test substitute with documented GPU
exception. Production user-path verification remains required after merge.

**Automated smoke preference**: For user-facing, routed, deployed, or
operational changes, prefer automated smoke in this order: development branch
profile; production synthetic smoke or one-off in-cluster Job; scriptable
Gateway/DNS/browser smoke against the exact user URL; manual browser checks only
as supplemental evidence.

**Completion evidence**: For deploy follow-up, record source fetched SHA, target
kustomization or HelmRelease applied SHA, live resource spec, Gateway/listener
match when applicable, and exact user-facing URL result.

**Fanout plan**: Three read-only lanes verify revisions, rollout/storage/init,
and user paths/observability. Main owns tracked edits and `evidence.md`.

**Evidence destination**: `specs/jellyfin-helm-client-apply/evidence.md`.

## Documentation Impact

None. The migration decision is unchanged; this is a Helm action-mode repair.

## Implementation Steps

1. Add failing full-render assertions for disabled upgrade/rollback SSA and no
   force.
2. Declare client-side apply for both Helm actions.
3. Run focused/repository checks, review-gated PR, and layered post-merge smoke.
4. Defer cleanup if any binding authentication gate remains unverified.

## Risks

| Risk | Mitigation |
| ---- | ---------- |
| Client-side apply differs from dry-run | Require production controller acceptance after merge. |
| Rollback inherits prior SSA behavior | Explicitly disable SSA for rollback too. |
| Force replacement increases blast radius | Assert force is absent. |
| Cleanup is premature | Keep it gated on full cutover and authentication evidence. |

## Complexity Tracking

> Fill only when the constitution check has a violation that must be justified.

| Violation | Why Needed | Simpler Alternative Rejected Because |
| --------- | ---------- | ------------------------------------ |
| N/A | N/A | N/A |
