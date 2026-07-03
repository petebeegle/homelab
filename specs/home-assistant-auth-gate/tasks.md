---
description: "Homelab SDD task list for Home Assistant auth gate"
---

# Tasks: home-assistant-auth-gate

**Input**: `specs/home-assistant-auth-gate/spec.md` and
`specs/home-assistant-auth-gate/plan.md`
**Risk Tier**: high
**Prerequisites**: Valid workflow marker, implementation plan, owner attestation,
and delegation token under `.codex/tmp/`

## Format: `[ID] [P?] [Req] Description`

- **[P]**: Can run in parallel because it touches different files and has no dependency on another task.
- **[Req]**: Requirement or user story trace, such as `FR-001` or `US1`.
- Include exact file paths in each task.

## Phase 1: Workflow Setup

- [x] T001 [FR-OWN] Create the sibling clone at `/workspaces/homelab-ideas/home-assistant-auth-gate` on `codex/home-assistant-auth-gate`.
- [x] T002 [FR-OWN] Create `.codex/tmp/active-implementation`, `.codex/tmp/implementation-plan.yaml`, `.codex/tmp/implementation-owner-attestation.yaml`, and matching delegation token evidence.
- [x] T003 [FR-OWN] Run the three owner workflow validators and record outcomes in `specs/home-assistant-auth-gate/evidence.md`.

## Phase 2: Spec And Plan

- [x] T004 [FR-SPEC] Write `specs/home-assistant-auth-gate/spec.md`.
- [x] T005 [FR-PLAN] Write `specs/home-assistant-auth-gate/plan.md`, including tiered TDD and development validation expectations.
- [x] T006 [FR-DOCS] Confirm documentation impact and generated architecture expectations.

## Phase 3: Implementation

- [x] T007 [P] [FR-001] Edit `kubernetes/apps/home-assistant/httproute.yaml` to remove `gateway/external`.
- [x] T008 [P] [FR-002] Rename package files and update generator keys in `kubernetes/apps/home-assistant/kustomization.yaml` and `kubernetes/apps/home-assistant/branch/kustomization.yaml`.
- [x] T009 [P] [FR-003] Edit `kubernetes/apps/synthetics/smoke/routes.spec.js` to fail onboarding explicitly.
- [x] T010 [P] [FR-004] Edit `docs/runbooks/home-assistant.md` to document withheld external exposure.
- [x] T011 [FR-IMPL] Refresh generated `docs/architecture.md` if renderer output changes.
- [x] T012 [FR-IMPL] Re-check constitution gates after implementation edits.

## Phase 4: Verification

- [x] T013 [FR-TEST] Run `kubectl kustomize kubernetes/apps/home-assistant`.
- [x] T014 [FR-TEST] Run `kubectl kustomize kubernetes/apps/home-assistant/branch`.
- [x] T015 [FR-TEST] Run `kubectl kustomize kubernetes/clusters/production/apps`.
- [x] T016 [FR-TEST] Run `npm --prefix kubernetes/apps/synthetics/smoke test`.
- [x] T017 [FR-TEST] Run `python3 tools/architecture/render.py --write` and `python3 tools/architecture/render.py --check`.
- [x] T018 [FR-TEST] Run targeted grep/render checks proving no external Home Assistant parentRef and no old hyphenated package slug remains.
- [ ] T019 [FR-SMOKE] Run development branch verifier for Home Assistant or record unavailable-infrastructure exception and substitutes.
- [x] T020 [FR-EVIDENCE] Record command outcomes, smoke evidence, exceptions, and final `HEAD` in `specs/home-assistant-auth-gate/evidence.md`.

## Phase 5: Commit And Handoff

- [x] T021 [FR-PR] Write `.codex/tmp/pr-summary.md` from the plan and final evidence.
- [x] T022 [FR-PR] Commit with a conventional commit message.
- [x] T023 [FR-PR] Report exact `HEAD` and do not create verifier approval.
