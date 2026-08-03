# Tasks: Fix Cilium Gateway CRD

**Input**: `specs/fix-cilium-gateway-crd/spec.md` and
`specs/fix-cilium-gateway-crd/plan.md`
**Risk Tier**: high
**Prerequisites**: Branch `codex/fix-cilium-gateway-crd` and matching approved
SDD artifacts.

## Human Gate Status

**Spec Gate**: Approved by the user through "fix" after the incident diagnosis.

**Plan Gate**: Approved by the same instruction because the previously proposed
repair sequence and this plan are equivalent in scope.

**Analyze Requirement**: Run before the source edit; implementation approval is
covered only if analysis finds no conflict or missing decision.

## Format: `[ID] [P?] [Req] Description`

- **[P]**: Can run in parallel or fan out to a helper lane.
- **[Req]**: Requirement or user-story trace.
- No tasks are marked `[P]` because this is one cluster-scoped dependency change
  and delegation was not requested.

## Phase 1: Setup And Baseline

- [x] T001 [FR-002] Create the dedicated branch/worktree and approved planning artifacts in `specs/fix-cilium-gateway-crd/`.
- [x] T002 [FR-006] Record the pre-change missing CRD, Cilium Operator prerequisite error, empty `cilium-secrets`, empty Envoy certificate set, TLS resets, and stale Proxmox telemetry in `specs/fix-cilium-gateway-crd/research.md`.
- [x] T003 [FR-007] Run Spec Kit analyze against `specs/fix-cilium-gateway-crd/spec.md`, `plan.md`, and `tasks.md` before editing Kubernetes desired state.

## Phase 2: User Story 1 — Restore Routed Services (P1)

**Goal**: Restore valid TLS handshakes and HTTP responses through the shared
Cilium internal Gateway.

**Independent Test**: After sequential development base reconciliation,
`https://whoami.dev.lab.petebeegle.com` completes TLS and returns a non-5xx HTTP
response.

- [x] T004 [US1] [FR-001] Add the Gateway API v1.5.1 standard BackendTLSPolicy CRD URL to `kubernetes/infra/crds/kustomization.yaml`.
- [x] T005 [US1] [FR-003] Review the source diff and assert no Gateway, route, certificate, alert, application, or unrelated CRD definitions changed outside `kubernetes/infra/crds/kustomization.yaml`.
- [x] T006 [US1] [FR-004] Render `kubernetes/infra/crds`, `kubernetes/clusters/development`, and `kubernetes/clusters/production`; assert the BackendTLSPolicy CRD appears exactly once in the shared render and each cluster activates `./kubernetes/infra/crds` exactly once.
- [x] T007 [US1] [FR-005] Run server-side dry-run validation against the development cluster for the shared CRD Kustomization and record the result in `specs/fix-cilium-gateway-crd/evidence.md`.
- [ ] T008 [US1] [FR-005] Commit and push the branch, then run `tools/development/verify_branch_deploy.py` for whoami with `--include-cluster-base`; record exact HEAD, route result, and cleanup in `specs/fix-cilium-gateway-crd/evidence.md`.
- [ ] T009 [US1] [FR-005] If development Cilium does not rediscover the API dynamically, restart only its operator and repeat controller, certificate-sync, and exact HTTPS checks; record whether restart was required in `specs/fix-cilium-gateway-crd/evidence.md`.

## Phase 3: User Story 2 — Restore Dependent Telemetry (P2)

**Goal**: Restore routed OTLP ingestion and allow telemetry-derived alerts to
reflect current infrastructure state.

**Independent Test**: `https://otel.lab.petebeegle.com` completes TLS and a new
Proxmox metric sample appears after recovery.

- [ ] T010 [US2] [FR-002] Apply the committed CRD manifest to production through the documented GitOps path or record any temporary incident-recovery apply explicitly in `specs/fix-cilium-gateway-crd/evidence.md`.
- [ ] T011 [US2] [FR-006] Restart only the production Cilium Operator if startup discovery requires it, then verify the live CRD, non-empty `cilium-secrets`, non-empty Envoy certificates, and absence of the prerequisite error.
- [ ] T012 [US2] [FR-006] Probe production whoami and OTLP HTTPS hostnames, query Mimir for a post-recovery Proxmox sample, and inspect the next synthetic summary and active Grafana alerts.

## Phase 4: Cross-Cutting Verification And Handoff

- [ ] T013 [FR-007] Run `python3 tools/architecture/render.py --check` and repository pre-commit checks for all changed files.
- [ ] T014 [FR-002] Re-check all constitution gates and audit `git diff` for plaintext secrets or unrelated changes.
- [ ] T015 [FR-007] Run Spec Kit converge and incorporate any remaining work into `specs/fix-cilium-gateway-crd/tasks.md` before final evidence.
- [ ] T016 [FR-007] Complete `specs/fix-cilium-gateway-crd/evidence.md` with commands, outcomes, exceptions, SHAs, user-path URLs, smoke cleanup, live recovery layers, and final HEAD.
- [ ] T017 [FR-002] Commit final evidence with a conventional commit and push `codex/fix-cilium-gateway-crd`.
- [ ] T018 [FR-002] Open a draft PR against `main` and report the review/merge requirement plus any temporary production recovery state.

## Dependencies

```text
T001-T002 -> T003 -> T004-T007 -> T008-T009 -> T010-T012 -> T013-T018
                          US1                         US2
```

- Analysis gates the source edit.
- User Story 1 is the minimum viable repair and must pass in development before
  any production recovery action.
- User Story 2 depends on the same routed TLS path and follows User Story 1.
- Final evidence and PR handoff depend on both story phases.

## Implementation Strategy

1. Prove the failing prerequisite and requirements consistency.
2. Make the one-line desired-state change and validate all rendered entrypoints.
3. Prove the shared base and exact HTTPS path in development.
4. Recover production with the narrowest necessary operator action.
5. Verify telemetry and alerts independently, then converge evidence and publish
   the reviewed GitOps change.

## Task Summary

- Total tasks: 18
- Setup/foundational tasks: 3
- User Story 1 tasks: 6
- User Story 2 tasks: 3
- Cross-cutting and handoff tasks: 6
- Parallel opportunities: none declared
- Suggested MVP: User Story 1 through T009
- Format validation: all tasks use checkboxes, sequential IDs, requirement or
  story labels, and concrete paths or commands.
