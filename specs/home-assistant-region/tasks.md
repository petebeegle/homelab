# Tasks: home-assistant-region

**Input**: `specs/home-assistant-region/spec.md` and
`specs/home-assistant-region/plan.md`
**Risk Tier**: high
**Prerequisites**: Valid workflow marker, implementation plan, owner
attestation, and delegation token under `.codex/tmp/`

## Phase 1: Workflow Setup

- [x] T001 [FR-OWN] Create the sibling clone on
      `codex/home-assistant-region`.
- [x] T002 [FR-OWN] Create `.codex/tmp/active-implementation`,
      `.codex/tmp/implementation-plan.yaml`,
      `.codex/tmp/implementation-owner-attestation.yaml`, and matching
      delegation token evidence.
- [x] T003 [FR-OWN] Run owner workflow validators.

## Phase 2: Spec And Plan

- [x] T004 [FR-SPEC] Write `specs/home-assistant-region/spec.md`.
- [x] T005 [FR-PLAN] Write `specs/home-assistant-region/plan.md`.
- [x] T006 [FR-DOCS] Confirm documentation impact.

## Phase 3: Implementation

- [x] T007 [FR-002] Create and encrypt
      `kubernetes/apps/home-assistant/secret.yaml`.
- [x] T008 [FR-001] Update
      `kubernetes/apps/home-assistant/config/configuration.yaml`.
- [x] T009 [FR-002] Update
      `kubernetes/apps/home-assistant/deployment.yaml`.
- [x] T010 [FR-002] Update
      `kubernetes/apps/home-assistant/kustomization.yaml`.
- [x] T011 [FR-003] Update
      `kubernetes/clusters/production/apps/home-assistant.yaml`.
- [x] T012 [FR-004] Update
      `kubernetes/apps/home-assistant/branch/config/configuration.yaml`.
- [x] T013 [FR-DOCS] Update `docs/runbooks/home-assistant.md`.

## Phase 4: Verification

- [x] T014 [FR-005] Run SOPS verification.
- [x] T015 [FR-005] Run production and branch Kustomize render checks.
- [x] T016 [FR-005] Run generated architecture check.
- [x] T017 [FR-005] Run development smoke validation or record exception.
- [x] T018 [FR-EVIDENCE] Record command outcomes, smoke evidence, exceptions,
      and final `HEAD` in `specs/home-assistant-region/evidence.md`.

## Phase 5: Commit And Handoff

- [x] T019 [FR-PR] Write `.codex/tmp/pr-summary.md` from the plan and final
      evidence.
- [x] T020 [FR-PR] Commit with a conventional commit message.
- [ ] T021 [FR-PR] Report exact `HEAD` and do not create verifier approval.
