---
description: "Homelab SDD task list for Elgato lighting in Home Assistant"
---

# Tasks: home-assistant-elgato-lighting

**Input**: `specs/home-assistant-elgato-lighting/spec.md` and
`specs/home-assistant-elgato-lighting/plan.md`
**Risk Tier**: medium
**Prerequisites**: Branch `codex/home-assistant-elgato-lighting` and matching
`specs/home-assistant-elgato-lighting/` artifacts.

## Format: `[ID] [P?] [Req] Description`

- **[P]**: Can run in parallel because it touches different files and has no
  dependency on another task.
- **[Req]**: Requirement or user story trace, such as `FR-001` or `US1`.
- Include exact file paths in each task.

## Phase 1: Spec And Plan

- [x] T001 [FR-SPEC] Create
      `specs/home-assistant-elgato-lighting/spec.md`.
- [x] T002 [FR-PLAN] Create
      `specs/home-assistant-elgato-lighting/plan.md`, including tiered TDD and
      development validation expectations.
- [x] T003 [FR-DOCS] Confirm documentation impact and generated architecture
      expectations.
- [x] T013 [FR-SPEC] Revise SDD artifacts from docs-only/tiny to medium-risk
      Home Assistant app behavior/config.
- [x] T014 [FR-PLAN] Update `.codex/tmp/implementation-plan.yaml` to match the
      new automation scope and validation expectations.

## Phase 2: Implementation

- [x] T004 [FR-001] [FR-002] Add Elgato discovery and manual setup guidance to
      `docs/runbooks/home-assistant.md`.
- [x] T005 [FR-003] [FR-004] Add Elgato entity inventory and runtime-state
      safety guidance to `docs/runbooks/home-assistant.md`.
- [x] T015 [FR-001] Add `input_boolean.desk_light_auto_balance` to
      `kubernetes/apps/home-assistant/config/packages/code_first.yaml`.
- [x] T016 [FR-002] [FR-003] Add the illuminance-triggered, helper-gated
      automation to `kubernetes/apps/home-assistant/config/packages/code_first.yaml`.
- [x] T017 [FR-004] [FR-005] [FR-006] [FR-007] [FR-008] [FR-009] Configure the
      required Elgato targets, transition, brightness percentages, kelvin
      values, and lux thresholds.
- [x] T018 [FR-010] Mirror the helper and automation in
      `kubernetes/apps/home-assistant/branch/config/packages/code_first.yaml`.
- [x] T019 [FR-DOCS] Update `docs/runbooks/home-assistant.md` only as needed to
      reflect the Git-owned automation.
- [x] T020 [FR-011] Re-check constitution gates after implementation edits.

## Phase 3: Verification

- [x] T007 [FR-TEST] Run
      `kubectl kustomize kubernetes/apps/home-assistant`.
- [x] T008 [FR-TEST] Run
      `kubectl kustomize kubernetes/apps/home-assistant/branch`.
- [x] T009 [FR-SMOKE] Record prior docs-only development smoke exception before
      the automation scope change; superseded by T025.
- [x] T010 [FR-EVIDENCE] Record command outcomes, smoke evidence, exceptions,
      and final `HEAD` in `specs/home-assistant-elgato-lighting/evidence.md`.
- [x] T021 [FR-TEST] Run
      `kubectl kustomize kubernetes/apps/home-assistant`.
- [x] T022 [FR-TEST] Run
      `kubectl kustomize kubernetes/apps/home-assistant/branch`.
- [x] T023 [FR-TEST] Run a YAML/config sanity check for the edited Home
      Assistant package files.
- [x] T024 [FR-TEST] Run workflow validators for the implementation owner
      context.
- [x] T025 [FR-SMOKE] Record development validation evidence or an
      unavailable-infrastructure exception with substitute checks.
- [x] T026 [FR-EVIDENCE] Record exact command outcomes, `git status --short`,
      docs impact, exceptions, and final `HEAD` in
      `specs/home-assistant-elgato-lighting/evidence.md`.

## Phase 4: Commit And PR

- [x] T011 [FR-PR] Commit with a conventional commit message.
- [x] T027 [FR-PR] Commit the automation change with a conventional commit
      message.
- [ ] T012 [FR-PR] Push branch `codex/home-assistant-elgato-lighting` and open
      a PR after separate verifier approval.
