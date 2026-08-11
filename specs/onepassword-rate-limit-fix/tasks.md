# Tasks: 1Password Rate-Limit Fix

**Input**: `spec.md` and `plan.md`
**Risk Tier**: high

## Human Gate Status

**Spec Gate**: Approved by direct incident-fix instruction.

**Plan Gate**: Expedited approval covered by the same instruction after reporting the measured cause and correction.

**Analyze Requirement**: Manual cross-artifact analysis before implementation.

## Phase 1: Setup and diagnosis

- [x] T001 [FR-006] Confirm live Deployment and OnePasswordItem state in both clusters.
- [x] T002 [FR-006] Verify account and token quota metadata without displaying credentials.
- [x] T003 [FR-006] Create the isolated branch, worktree, and SDD artifacts.
- [x] T004 [FR-ANALYZE] Cross-check spec, plan, requirements, and acceptance.

## Phase 2: Tests and implementation

- [x] T005 [FR-002] Add a failing regression test for 300 seconds in `tools/policy/tests/test_check_onepassword_production_foundation.py`.
- [x] T006 [FR-002] Enforce production 3600 seconds and development 31536000 seconds in `tools/policy/check_onepassword_production_foundation.py`.
- [x] T007 [FR-001] Parameterize shared values and add cluster-specific substitutions.
- [x] T008 [FR-005] Document rate-limit diagnosis and recovery in the runbook.
- [x] T009 [FR-003] Re-check constitution and direct-auth/Connect invariants.

## Phase 3: Verification

- [x] T010 [FR-002] Run focused policy tests and checker.
- [x] T011 [FR-003] Run the direct-auth chart validator.
- [x] T012 [FR-003] Strictly render/substitute both entrypoints and run schema/policy checks.
- [x] T013 [FR-006] Run architecture and harness/SDD checks.
- [x] T014 [FR-001] Push exact HEAD and validate the development base/operator plus annotation-triggered refresh.
- [x] T015 [FR-CONVERGE] Reconcile discoveries into the artifacts.
- [x] T016 [FR-006] Complete `evidence.md` without secret material.

## Phase 4: Commit and PR

- [x] T017 [FR-PR] Commit with a conventional commit message.
- [ ] T018 [FR-PR] Push and open the pull request.
