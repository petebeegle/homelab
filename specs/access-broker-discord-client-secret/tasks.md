# Tasks: access-broker-discord-client-secret

**Input**: `specs/access-broker-discord-client-secret/spec.md` and
`specs/access-broker-discord-client-secret/plan.md`
**Risk Tier**: medium

## Human Gate Status

**Spec Gate**: Approved by direct user instruction.
**Plan Gate**: Approved by direct user instruction.
**Analyze Requirement**: Skipped with rationale in evidence.

## Phase 1: Implementation

- [x] T001 [FR-001] Add encrypted `DISCORD_CLIENT_SECRET` to
      `kubernetes/apps/access-broker/secret.yaml`.
- [x] T002 [FR-002] Confirm no plaintext secret is present.

## Phase 2: Verification

- [x] T003 [FR-TEST] Run SOPS file status check.
- [x] T004 [FR-TEST] Run access-broker render check.
- [ ] T005 [FR-SMOKE] Verify public callback behavior after merge.
- [x] T006 [FR-EVIDENCE] Record command outcomes.

## Phase 3: Commit And PR

- [ ] T007 [FR-PR] Commit, push, open PR, and merge after checks.
