# Tasks: access-broker-authentik-token

**Input**: `specs/access-broker-authentik-token/spec.md` and
`specs/access-broker-authentik-token/plan.md`
**Risk Tier**: medium

## Human Gate Status

**Spec Gate**: Approved by ongoing user instruction.
**Plan Gate**: Approved by ongoing user instruction.
**Analyze Requirement**: Skipped with rationale in evidence.

## Phase 1: Implementation

- [x] T001 [FR-001] Add encrypted `AUTHENTIK_TOKEN` to
      `kubernetes/apps/access-broker/secret.yaml`.
- [x] T002 [FR-003] Update rollout annotation in
      `kubernetes/apps/access-broker/deployment.yaml`.

## Phase 2: Verification

- [x] T003 [FR-TEST] Run SOPS file status check.
- [x] T004 [FR-TEST] Run app render check.
- [x] T005 [FR-TEST] Run plaintext token and no-Ingress scans.
- [ ] T006 [FR-SMOKE] Verify live deployment after merge.
- [x] T007 [FR-EVIDENCE] Record command outcomes.

## Phase 3: Commit And PR

- [ ] T008 [FR-PR] Commit, push, open PR, and merge after checks.
