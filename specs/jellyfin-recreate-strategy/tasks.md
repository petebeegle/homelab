# Tasks: Jellyfin Recreate Strategy

## Phase 1: Setup and baseline

- [X] T001 Record the production Helm failure and safe rollback baseline in
  `specs/jellyfin-recreate-strategy/evidence.md`.
- [X] T002 Add Helm setup for the focused Jellyfin test in
  `.github/workflows/ci.yml`.

## Phase 2: User Story 1 - Valid migration rollout

**Goal**: Render and apply a valid RollingUpdate-to-Recreate transition.

**Independent test**: Pinned chart output contains an explicit
`rollingUpdate: null` and `type: Recreate` in the Deployment strategy.

- [X] T003 [US1] Extend
  `tools/development/tests/test_jellyfin_config_migration.py` with a failing
  pinned-chart strategy regression.
- [X] T004 [US1] Record the expected merged-baseline failure in
  `specs/jellyfin-recreate-strategy/evidence.md`.
- [X] T005 [US1] Add the explicit rolling-update clear to
  `kubernetes/apps/jellyfin/values.yaml`.
- [X] T006 [US1] Run the focused test and exact Helm render, recording passing
  output in `specs/jellyfin-recreate-strategy/evidence.md`.

## Phase 3: User Story 2 - Preserve safeguards

**Goal**: Prove the transition repair does not alter migration, storage,
authentication, scheduling, or rollback contracts.

**Independent test**: Focused assertions and diff review show only the intended
strategy transition while all existing migration cases pass.

- [X] T007 [US2] Add or retain rendered invariant assertions for local target,
  read-only NFS source, init ordering, and GPU selection in
  `tools/development/tests/test_jellyfin_config_migration.py`.
- [X] T008 [US2] Run architecture, SDD context, diff, and pre-commit validation;
  record results in `specs/jellyfin-recreate-strategy/evidence.md`.

## Phase 4: Review and production acceptance

- [X] T009 Push the implementation, open a draft PR, and require all GitHub
  status checks before merge; record the PR in
  `specs/jellyfin-recreate-strategy/evidence.md`.
- [ ] T010 [P] Verify the merged/fetched/applied revision and Helm conditions in
  production; record exact timestamps in
  `specs/jellyfin-recreate-strategy/evidence.md`.
- [ ] T011 [P] Verify live Deployment strategy, PVCs, migration init/marker,
  application readiness, and storage/GPU state in
  `specs/jellyfin-recreate-strategy/evidence.md`.
- [ ] T012 [P] Verify exact web/SSO-start paths and relevant logs/observability,
  recording authenticated limitations in
  `specs/jellyfin-recreate-strategy/evidence.md`.
- [ ] T013 Consolidate acceptance and decide whether cleanup is authorized; do
  not remove assets in this implementation unless every binding gate is proven.

## Dependencies

- T001-T004 establish baseline and regression before T005.
- T005 blocks T006-T009.
- T009 and merge block T010-T013.
- T010-T012 are independent read-only fanout lanes; T013 consolidates them.

## Implementation strategy

The MVP is User Story 1: one values field plus a pinned chart regression. User
Story 2 and production acceptance are required before completion because the
change affects a live storage migration.
