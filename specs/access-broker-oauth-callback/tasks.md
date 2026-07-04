# Tasks: access-broker-oauth-callback

**Input**: `specs/access-broker-oauth-callback/spec.md` and
`specs/access-broker-oauth-callback/plan.md`
**Risk Tier**: medium
**Prerequisites**: Branch `codex/access-broker-oauth-callback` and matching
Spec Kit artifacts.

## Human Gate Status

**Spec Gate**: Approved by direct user implementation instruction.

**Plan Gate**: Approved by direct user implementation instruction.

**Analyze Requirement**: Skipped with rationale recorded in evidence.

## Phase 1: Setup

- [x] T001 [FR-SETUP] Confirm branch, fallback worktree, and approved scope.
- [x] T002 [FR-SETUP] Confirm `homelab-access` OAuth callback PR #5 is merged.

## Phase 2: Implementation

- [x] T003 [FR-001] Edit `kubernetes/apps/access-broker/configmap.yaml`.
- [x] T004 [FR-002] Edit `kubernetes/apps/access-broker/deployment.yaml`.
- [x] T005 [FR-003] Re-check constitution gates after implementation edits.

## Phase 3: Verification

- [x] T006 [FR-TEST] Run `kubectl kustomize kubernetes/apps/access-broker`.
- [x] T007 [FR-TEST] Run `kubectl kustomize kubernetes/clusters/production`.
- [x] T008 [FR-TEST] Run no-Ingress and plaintext-secret scans.
- [x] T009 [FR-SMOKE] Record development validation exception.
- [x] T010 [FR-CONVERGE] Record skipped-converge rationale.
- [x] T011 [FR-EVIDENCE] Record command outcomes and final `HEAD`.

## Phase 4: Commit And PR

- [ ] T012 [FR-PR] Commit with a conventional commit message.
- [ ] T013 [FR-PR] Push branch and open a PR.
