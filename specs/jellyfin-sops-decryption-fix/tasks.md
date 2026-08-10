# Tasks: Jellyfin SOPS Decryption Fix

**Input**: `specs/jellyfin-sops-decryption-fix/spec.md` and `plan.md`
**Risk Tier**: high
**Prerequisites**: Branch `codex/jellyfin-sops-decryption-fix`; user-approved narrow prerequisite scope.

## Human Gate Status

**Spec Gate**: Approved by the user on 2026-08-10.

**Plan Gate**: Approved by the same explicit response to the stated one-stanza separate-PR approach and no-output acceptance.

**Analyze Requirement**: Run before source implementation; remediate any critical or high findings before editing the production Flux resource.

## Phase 1: Setup And Failing Evidence

- [x] T001 [FR-001] Create the matching branch/worktree and complete SDD artifacts under `specs/jellyfin-sops-decryption-fix/`.
- [x] T002 [FR-003] Record a status-only comparison proving committed Jellyfin and Authentik OAuth plaintext equality in `specs/jellyfin-sops-decryption-fix/evidence.md`.
- [x] T003 [FR-001] Capture the pre-change structural assertion that `kubernetes/clusters/production/apps/jellyfin.yaml` lacks `spec.decryption`.
- [x] T004 [FR-006] Run Spec Kit analyze across `spec.md`, `plan.md`, and `tasks.md` before the source edit.

## Phase 2: User Story 1 - Restore Secret Reconciliation

**Story Goal**: Production Jellyfin receives the same plaintext OAuth client secret used by Authentik.

**Independent Test**: Render and structurally assert the exact Flux decryption configuration; committed and post-merge live comparisons report equality without values.

- [x] T005 [US1] Add SOPS provider and `sops-age` Secret reference to `kubernetes/clusters/production/apps/jellyfin.yaml`.
- [x] T006 [US1] Assert `app-jellyfin` renders exactly one correct decryption configuration from `kubernetes/clusters/production/`.
- [x] T007 [US1] Assert encrypted Secret documents and all Jellyfin/Authentik consumers are unchanged relative to `origin/main`.

## Phase 3: Verification And Evidence

- [x] T008 [P] [FR-003] Repeat the no-output committed plaintext comparison and record status in `specs/jellyfin-sops-decryption-fix/evidence.md`.
- [x] T009 [P] [SC-001] Run production/development renders, policy checks, architecture check, harness tests, and full pre-commit.
- [x] T010 [FR-004] Record the production-only development-validation exception and substitute checks in `specs/jellyfin-sops-decryption-fix/evidence.md`.
- [x] T011 [FR-006] Run Spec Kit converge and append any genuinely remaining implementation work to `tasks.md`.
- [x] T012 [FR-004] Record validation results and pending exact-revision post-merge acceptance in `specs/jellyfin-sops-decryption-fix/evidence.md`.

## Phase 4: Commit, PR, And Deployment Gate

- [x] T013 [FR-002] Commit the scoped change with a conventional commit message.
- [x] T014 [FR-004] Push `codex/jellyfin-sops-decryption-fix` and open the gated PR.
- [ ] T015 [FR-004] After merge, reconcile exact main, require `app-jellyfin` Ready/applied, and prove live equality/non-envelope status without output.
- [ ] T016 [FR-006] Resume the separate `onepassword-dual-publish` implementation only after T015 passes.

## Dependencies

- T003 and T004 block T005.
- T005 blocks T006-T012.
- T013-T014 require local validation complete.
- T015 requires merge; T016 requires successful live acceptance.

## Parallel Opportunities

- T008 and T009 are read-only checks over distinct validation surfaces and may run independently, but no helper agents are used because the user did not request delegation.
