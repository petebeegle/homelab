---
description: "Homelab SDD task list for home-assistant-ui-automation"
---

# Tasks: home-assistant-ui-automation

**Input**: `specs/home-assistant-ui-automation/spec.md` and
`specs/home-assistant-ui-automation/plan.md`
**Risk Tier**: medium
**Prerequisites**: Branch `codex/home-assistant-ui-automation` and matching
`specs/home-assistant-ui-automation/` artifacts.

## Format: `[ID] [P?] [Req] Description`

- **[P]**: Can run in parallel because it touches different files and has no
  dependency on another task.
- **[Req]**: Requirement or user story trace, such as `FR-001` or `US1`.
- Include exact file paths in each task.

## Phase 1: Spec And Plan

- [x] T001 [FR-SPEC] Create `specs/home-assistant-ui-automation/spec.md`.
- [x] T002 [FR-PLAN] Create `specs/home-assistant-ui-automation/plan.md`,
      including tiered TDD and development validation expectations.
- [x] T003 [FR-DOCS] Confirm documentation impact and generated architecture
      expectations.
- [x] T004 [FR-WORKFLOW] Create local workflow marker, implementation plan,
      owner attestation, and delegation token evidence under `.codex/tmp/`.

## Phase 2: Implementation

- [x] T005 [FR-001,FR-002,FR-004] Edit
      `kubernetes/apps/home-assistant/config/packages/code_first.yaml`.
- [x] T006 [FR-003,FR-004] Edit
      `kubernetes/apps/home-assistant/branch/config/packages/code_first.yaml`.
- [x] T007 [FR-005] Update `docs/runbooks/home-assistant.md`.
- [x] T008 [FR-006] Re-check constitution gates after implementation edits.

## Phase 3: Verification

- [x] T009 [FR-007] Run `kubectl kustomize kubernetes/apps/home-assistant`.
- [x] T010 [FR-007] Run
      `kubectl kustomize kubernetes/apps/home-assistant/branch`.
- [x] T011 [FR-007] Run package parity diff between base and branch
      `code_first.yaml`.
- [x] T012 [FR-007] Run removed-identifier search for
      `desk_elgato_ambient_balance` and `desk_light_auto_balance` in
      Git-owned Home Assistant config.
- [x] T013 [FR-007] Run workflow validators for marker, implementation plan,
      owner attestation, and SDD context.
- [x] T014 [FR-007] Run `git diff --check` and `git status --short`.
- [x] T015 [FR-007] Run development smoke if feasible, or record exception and
      substitute checks.
- [x] T016 [FR-007] Record command outcomes, smoke evidence, exceptions, and
      final branch state in `specs/home-assistant-ui-automation/evidence.md`.

## Phase 4: Commit

- [x] T017 [FR-COMMIT] Commit with a conventional commit message.
- [x] T018 [FR-NOPUSH] Confirm branch is not pushed and no verifier approval is
      created.
