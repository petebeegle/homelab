# Tasks: access-broker-review-admins

**Input**: `specs/access-broker-review-admins/spec.md` and
`specs/access-broker-review-admins/plan.md`
**Risk Tier**: medium

## Human Gate Status

**Spec Gate**: Approved by ongoing user instruction.
**Plan Gate**: Approved by ongoing user instruction.
**Analyze Requirement**: Skipped with rationale in evidence.

## Phase 1: Implementation

- [x] T001 [FR-001] Add `DISCORD_ADMIN_USER_IDS` to
      `kubernetes/apps/access-broker/configmap.yaml`.
- [x] T002 [FR-002] Update rollout annotation in
      `kubernetes/apps/access-broker/deployment.yaml`.

## Phase 2: Verification

- [x] T003 [FR-TEST] Run app render check.
- [x] T004 [FR-TEST] Run production render check.
- [x] T005 [FR-TEST] Run no-Ingress scan.
- [ ] T006 [FR-SMOKE] Verify live deployment after merge.
- [x] T007 [FR-EVIDENCE] Record command outcomes.

## Phase 3: Commit And PR

- [ ] T008 [FR-PR] Commit, push, open PR, and merge after checks.
