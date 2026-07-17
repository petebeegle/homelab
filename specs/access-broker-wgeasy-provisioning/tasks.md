# Tasks: access-broker-wgeasy-provisioning

**Input**: `specs/access-broker-wgeasy-provisioning/spec.md` and
`specs/access-broker-wgeasy-provisioning/plan.md`

- [x] T001 [FR-SPEC] Create SDD artifacts for the rollout.
- [x] T002 [P] [FR-002] Confirm homelab-access PR #9 is merged and the main
      image workflow passed.
- [x] T003 [FR-001] Add `WGEASY_USERNAME` to
      `kubernetes/apps/access-broker/configmap.yaml`.
- [x] T004 [FR-002] Bump the access-broker rollout annotation in
      `kubernetes/apps/access-broker/deployment.yaml`.
- [x] T005 [P] [FR-TEST] Run access-broker and production render checks.
- [x] T006 [P] [FR-TEST] Run plaintext secret scans.
- [x] T007 [FR-EVIDENCE] Record validation, live-smoke blocker, and final HEAD
      in `specs/access-broker-wgeasy-provisioning/evidence.md`.
- [x] T008 [FR-PR] Commit, push, and open PR.
