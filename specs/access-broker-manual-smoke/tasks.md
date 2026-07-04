# Tasks: access-broker-manual-smoke

**Input**: `specs/access-broker-manual-smoke/spec.md` and
`specs/access-broker-manual-smoke/plan.md`
**Risk Tier**: high
**Prerequisites**: Branch `codex/access-broker-manual-smoke` and matching
`specs/access-broker-manual-smoke/` artifacts.

## Phase 1: Spec And Plan

- [x] T001 [FR-SPEC] Create `specs/access-broker-manual-smoke/spec.md`.
- [x] T002 [FR-PLAN] Create `specs/access-broker-manual-smoke/plan.md`.
- [x] T003 [FR-DOCS] Confirm architecture/doc impact.

## Phase 2: Implementation

- [x] T004 [FR-001,FR-003] Configure access-broker hostname and HTTPRoute.
- [x] T005 [FR-004] Add Discord app identity and SOPS-encrypt access-broker Secret.
- [x] T006 [FR-002] Add Cloudflare Tunnel ingress for `onboard.petebeegle.com`.
- [x] T007 [FR-005] Activate production Flux Kustomization for access-broker.
- [x] T008 [FR-IMPL] Re-check constitution gates after edits.

## Phase 3: Verification

- [x] T009 [FR-TEST] Run access-broker render/assertions.
- [x] T010 [FR-TEST] Run cloudflare-tunnels render/assertions.
- [x] T011 [FR-TEST] Run production cluster render.
- [x] T012 [FR-TEST] Run architecture check/update.
- [x] T013 [FR-TEST] Run secret and Ingress scans.
- [x] T014 [FR-TEST] Run SDD context validator.
- [x] T015 [FR-SMOKE] Record development-smoke exception and manual production smoke handoff.
- [x] T016 [FR-EVIDENCE] Record evidence in `specs/access-broker-manual-smoke/evidence.md`.

## Phase 4: Commit And PR

- [x] T017 [FR-PR] Commit homelab changes.
- [x] T018 [FR-PR] Push branch and open PR.
