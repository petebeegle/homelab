# Tasks: Jellyfin Helm Client Apply

## Phase 1: Baseline

- [X] T001 Record PR #385 terminal SSA failure and safe rollback in
  `specs/jellyfin-helm-client-apply/evidence.md`.
- [X] T002 [US1] Add failing upgrade/rollback apply-mode and no-force assertions
  to `tools/development/tests/test_jellyfin_config_migration.py`.
- [X] T003 [US1] Record the expected baseline regression failure in
  `specs/jellyfin-helm-client-apply/evidence.md`.

## Phase 2: User Story 1 - Strategy transition applies

- [X] T004 [US1] Set upgrade and rollback `serverSideApply: disabled` in
  `kubernetes/apps/jellyfin/app.yaml` without enabling force.
- [X] T005 [US1] Run the focused render/migration suite and record results in
  `specs/jellyfin-helm-client-apply/evidence.md`.

## Phase 3: User Story 2 - Preserve cutover safety

- [X] T006 [US2] Verify diff and existing storage/init/GPU/auth assertions remain
  green in `tools/development/tests/test_jellyfin_config_migration.py`.
- [X] T007 [US2] Run architecture, SDD context, pre-commit, and diff validation;
  record it in `specs/jellyfin-helm-client-apply/evidence.md`.

## Phase 4: Review and production acceptance

- [X] T008 Push, open a draft PR, and require all GitHub checks; record PR data
  in `specs/jellyfin-helm-client-apply/evidence.md`.
- [ ] T009 [P] Verify merged/fetched/applied revision and Helm conditions in
  `specs/jellyfin-helm-client-apply/evidence.md`.
- [ ] T010 [P] Verify live Recreate strategy, local/NFS storage, migration init,
  marker, pod/GPU/events in `specs/jellyfin-helm-client-apply/evidence.md`.
- [ ] T011 [P] Verify exact web/SSO paths, logs, and observability with auth
  limitations in `specs/jellyfin-helm-client-apply/evidence.md`.
- [ ] T012 Consolidate cleanup eligibility; retain all migration assets if any
  binding acceptance remains unverified.

## Dependencies

- T001-T003 precede T004.
- T004 precedes T005-T008.
- T008 and merge precede parallel T009-T011; T012 consolidates them.

## Implementation strategy

One HelmRelease behavior change plus focused regression is the MVP. Production
acceptance remains required because this is the live storage cutover boundary.
