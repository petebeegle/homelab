---
description: "Dependency-ordered portfolio backlog for completing homelab access"
---

# Tasks: Access Broker Delivery Roadmap

**Input**: `specs/access-broker-roadmap/spec.md` and
`specs/access-broker-roadmap/plan.md`
**Risk Tier**: low for roadmap planning; each future slice declares its own
medium/high tier
**Prerequisites**: Branch `codex/access-broker-roadmap` and matching planning
artifacts. This task list authorizes no implementation until the roadmap's
human gates are approved.

## Human Gate Status

**Spec Gate**: Approved by the user on 2026-07-25.

**Plan Gate**: Approved by the user on 2026-07-25.

**Analyze Requirement**: Completed with no critical consistency findings and
approved by the user on 2026-07-25; each future homelab slice repeats analyze
in its own Spec Kit workflow.

## Format: `[ID] [P?] [Req] Description`

- **[P]**: Safe to execute concurrently after declared prerequisites because
  the task owns a disjoint repository/package or performs read-only validation.
- **[US1]**: Prioritized delivery sequence.
- **[US2]**: Conflict-aware parallel work.
- **[US3]**: Verifiable incremental releases.
- App-only tasks use one app branch and PR with equivalent scope/test/smoke
  evidence in the PR. Homelab tasks additionally use a matching
  `specs/<implementation>/` workflow.

## Phase 1: Roadmap Gates

- [x] T001 [US1] Review and approve intended scope, non-goals, milestones, and
  requirements in `specs/access-broker-roadmap/spec.md`.
- [x] T002 [US2] Review and approve delivery waves, write-scope ownership, and
  dependency graph in `specs/access-broker-roadmap/plan.md`.
- [ ] T003 [P] [US1] Resolve DG-001 activation model in the future
  `specs/access-broker-authentik-activation-gitops/spec.md` before S11/S12.
- [ ] T004 [P] [US1] Resolve DG-002 default grant lifetime in the future
  `specs/access-broker-grant-expiration/spec.md` before S17.
- [ ] T005 [P] [US1] Resolve DG-003 initial access bundle in the future
  `specs/access-broker-authentik-entitlement/spec.md` before S05/S12.
- [x] T006 [US3] Approve the roadmap task/analysis gate using
  `specs/access-broker-roadmap/tasks.md` and the Spec Kit analysis report.

## Phase 2: Wave 1 Foundations

**Goal**: Establish safe application contracts and deterministic releases
before feature fanout.

**Independent Test**: Concurrent approval claims produce one active grant, and a
reviewed app commit is deployed by immutable digest with deterministic
configuration rollout.

- [ ] T007 [P] [US1] Deliver S01 `access-broker-domain-foundation` in
  `/home/vscode/homelab-access/internal/access/`,
  `/home/vscode/homelab-access/internal/server/commands/`, and focused tests,
  including atomic claim and one-active-grant behavior.
- [ ] T008 [P] [US3] Deliver S02A `access-broker-immutable-images` in
  `/home/vscode/homelab-access/.github/workflows/ci.yml` and
  `/home/vscode/homelab-access/Dockerfile`, publishing commit-addressed images
  with OCI revision metadata.
- [ ] T009 [US3] Deliver S02B `access-broker-release-hygiene` after T008 using
  `kubernetes/apps/access-broker/deployment.yaml`,
  `kubernetes/apps/access-broker/secret.yaml`, update automation configuration,
  and `specs/access-broker-release-hygiene/`.

## Phase 3: Wave 2 Module Fanout

**Goal**: Build disjoint policy, provider, persistence, delivery, and telemetry
modules against merged S01 contracts.

**Independent Test**: Each lane passes focused contract tests without editing
another lane's owned package or central integration files.

- [ ] T010 [P] [US1] Deliver S03 `access-broker-intake-guard` in
  `/home/vscode/homelab-access/internal/config/`,
  `/home/vscode/homelab-access/internal/discord/`, and new focused handler
  files, proving disallowed contexts mutate no state.
- [ ] T011 [P] [US1] Deliver S04 `access-broker-provider-lifecycle` in
  `/home/vscode/homelab-access/internal/authentik/` and
  `/home/vscode/homelab-access/internal/wgeasy/`, including stable-ID lookup,
  entitlement reconciliation, revoke, and rotate contracts.
- [ ] T012 [P] [US1] Deliver S05 `access-broker-authentik-entitlement` after
  T005 using a new file under `kubernetes/infra/authentik/blueprints/`, blueprint
  registration, and `specs/access-broker-authentik-entitlement/`.
- [ ] T013 [P] [US2] Deliver S06 `access-broker-postgres-repository` in
  `/home/vscode/homelab-access/internal/persistence/` with schema, transactional
  repository, partial uniqueness, JSON importer, and migration fixtures.
- [ ] T014 [P] [US1] Deliver S07 `access-broker-requester-delivery` in
  `/home/vscode/homelab-access/internal/artifacts/`,
  `/home/vscode/homelab-access/internal/delivery/`, and requester-owned status
  command files.
- [ ] T015 [P] [US3] Deliver S08 `access-broker-audit-metrics` in
  `/home/vscode/homelab-access/internal/audit/` and
  `/home/vscode/homelab-access/internal/metrics/`, with bounded-cardinality
  metrics and secret-free structured events.
- [ ] T016 [US2] Audit active Wave 2 branches against
  `specs/access-broker-roadmap/contracts/roadmap-slice.md` before shared
  integration begins.

## Phase 4: Wave 3 Durable Runtime And Desired State

**Goal**: Integrate transactional persistence, recoverable jobs, and the chosen
identity activation model.

**Independent Test**: Provisioning survives a crash after every external side
effect without duplicating users, entitlements, or peers; migration and
activation pass in development.

- [ ] T017 [P] [US3] Deliver S09 `access-broker-postgres-deployment` after T009
  and T013 using `kubernetes/apps/access-broker/`, encrypted credentials,
  backup/migration desired state, and
  `specs/access-broker-postgres-deployment/`.
- [ ] T018 [P] [US2] Deliver S10 `access-broker-durable-jobs` after T011, T013,
  and T015 using `/home/vscode/homelab-access/internal/jobs/`,
  `/home/vscode/homelab-access/cmd/homelab-access/`, and the single central
  integration owner.
- [ ] T019 [P] [US1] Deliver S11 `access-broker-authentik-activation-app` after
  T003, T013, T014, and T018 using
  `/home/vscode/homelab-access/internal/authentik/activation.go` and private
  delivery contracts.
- [ ] T020 [US1] Deliver S12 `access-broker-authentik-activation-gitops` after
  T012 and T019 using `kubernetes/infra/authentik/blueprints/`, any approved
  route/secret changes, and
  `specs/access-broker-authentik-activation-gitops/`.

## Phase 5: Wave 4 Minimum Viable Multi-User Service

**Goal**: Complete private requester delivery, lifecycle commands, intake
deployment, and exact-path acceptance.

**Independent Test**: A non-admin requester in the allowed Discord context
requests access, receives it privately, downloads once, connects the VPN,
activates Authentik, and reaches only the approved application set.

- [ ] T021 [P] [US1] Deliver S13 `access-broker-discord-delivery` after T009,
  T014, and T018 using
  `/home/vscode/homelab-access/internal/discord/client.go` and delivery retry
  tests; retain requester status as blocked-DM fallback.
- [ ] T022 [US1] Deliver S14 `access-broker-command-lifecycle` after T011, T014,
  and T018 using `/home/vscode/homelab-access/internal/server/commands/` as the
  sole command integration owner for list, status, retry, reissue, and revoke.
- [ ] T023 [US3] Deliver S15 `access-broker-intake-deployment` after T009, T010,
  and T022 using `kubernetes/apps/access-broker/configmap.yaml`, encrypted
  configuration where required, and
  `specs/access-broker-intake-deployment/`.
- [ ] T024 [US3] Deliver S16 `access-broker-mvp-smoke` after T017 through T023
  using a development access-broker profile, exact-path synthetic or scripted
  smoke, cleanup, and `specs/access-broker-mvp-smoke/`.
- [ ] T025 [US1] Record M1 approval only after T024 proves the non-admin
  requester path and all unverified production-only layers are listed in
  `specs/access-broker-mvp-smoke/evidence.md`.

## Phase 6: Wave 5 Managed Lifecycle

**Goal**: Add expiration, secure cleanup, and explicit repeat-request policy.

**Independent Test**: Expiry and manual revocation remove VPN and entitlement,
consumed/expired secrets are absent, and repeat flows preserve one active grant.

- [ ] T026 [P] [US1] Deliver S17 `access-broker-grant-expiration` after T004,
  T018, and T022 using
  `/home/vscode/homelab-access/internal/jobs/expiration.go` and lifecycle policy
  tests.
- [ ] T027 [P] [US1] Deliver S18 `access-broker-artifact-cleanup` after T013 and
  T018 using `/home/vscode/homelab-access/internal/artifacts/` and persistence
  cleanup jobs that hash tokens and purge private configuration.
- [ ] T028 [US1] Deliver S19 `access-broker-repeat-request-policy` after T026
  and T027 using `/home/vscode/homelab-access/internal/access/` and focused
  request-policy command handlers.
- [ ] T029 [US3] Record M2 approval only after revocation partial-failure,
  expiration, reissue, rename, and purge evidence is consolidated in the
  owning slice evidence or PRs.

## Phase 7: Wave 6 Production Operations

**Goal**: Make service health, audit, command registration, restore, and final
security readiness operationally verifiable.

**Independent Test**: Real metrics and logs drive actionable alerts; commands
reconcile idempotently; backup/restore and revocation drills pass; final E2E
proves the exact running image and user path.

- [ ] T030 [P] [US3] Deliver S20 `access-broker-observability` after T015, T026,
  and T027 using `kubernetes/infra/monitoring/grafana/`, an operator runbook
  under `docs/runbooks/`, and `specs/access-broker-observability/`.
- [ ] T031 [P] [US3] Deliver S21 `access-broker-command-registration` after
  T022 using `/home/vscode/homelab-access/internal/discord/commands.go`,
  registration tooling, API read-back tests, and rotated bot credentials.
- [ ] T032 [P] [US3] Deliver S22A `access-broker-readiness-app` after T024,
  T026 through T028, and T031 using app load/concurrency tests, crash-recovery
  tests, and immutable release evidence in
  `/home/vscode/homelab-access/`.
- [ ] T033 [US3] Deliver S22B `access-broker-production-readiness` after T030
  and T032 using homelab restore and revocation drills, readiness release
  deployment, final end-to-end smoke, operator runbooks, and
  `specs/access-broker-production-readiness/`.
- [ ] T034 [US3] Record M3 approval only after T033 includes app image digest,
  homelab merge SHA, Flux fetched/applied SHA, live image ID, exact user path,
  provider cleanup, alert recovery, and temporary-resource cleanup.

## Phase 8: Roadmap Maintenance

- [ ] T035 [US2] Update `specs/access-broker-roadmap/plan.md` when a decision or
  merged slice changes dependencies, without folding implementation evidence
  into this roadmap.
- [ ] T036 [US2] Re-run the requirement coverage and dependency-cycle checks in
  `specs/access-broker-roadmap/quickstart.md` at each milestone.
- [ ] T037 [US3] Archive superseded assumptions and link merged PRs from
  `specs/access-broker-roadmap/evidence.md` at M1, M2, and M3.

## Dependencies

```text
Roadmap gates: T001 -> T002 -> T006
Decision gates: T003/T004/T005 may run in parallel
Foundations: T007 || T008; T008 -> T009
Module fanout: T007 -> T010/T011/T013/T014/T015; T005 -> T012
Integration: T009+T013 -> T017; T011+T013+T015 -> T018
Activation: T003+T013+T014+T018 -> T019; T012+T019 -> T020
MVP: T021 || T022, then T023, then T024 -> T025
Lifecycle: T026 || T027, then T028 -> T029
Operations: T030 || T031; T024+T026-T028+T031 -> T032; T030+T032 -> T033 -> T034
```

## Parallel Execution Examples

### Foundation

```text
Lane A: T007 domain foundation
Lane B: T008 immutable image publishing -> T009 GitOps release hygiene
```

### Module Fanout After T007

```text
Lane A: T010 intake policy
Lane B: T011 provider lifecycle
Lane C: T013 persistence
Lane D: T014 requester delivery
Lane E: T015 audit and metrics
Homelab lane: T012 Authentik entitlement
Integration gate: T016
```

### Lifecycle And Operations

```text
Lane A: T026 expiration
Lane B: T027 artifact cleanup
Then: T028 repeat policy

Lane C: T030 Grafana and runbook
Lane D: T031 command registration -> T032 application readiness
Then: T030 + T032 -> T033 production readiness
```

## Implementation Strategy

1. Merge foundations before allowing broad fanout.
2. Deliver M1 as the smallest safe service for another user.
3. Do not enable scheduled production provisioning smoke until deterministic
   revocation and cleanup exist at M2.
4. Treat M3 as operational hardening, not a prerequisite for a tightly
   allowlisted M1 pilot.

## Format Validation

- All tasks use checkbox, sequential task ID, story label, and concrete path or
  artifact.
- `[P]` appears only for declared disjoint lanes.
- Shared central app and homelab integration tasks are serialized.
