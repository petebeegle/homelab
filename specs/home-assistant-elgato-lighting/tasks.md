---
description: "Homelab SDD task list for Elgato lighting in Home Assistant"
---

# Tasks: home-assistant-elgato-lighting

**Input**: `specs/home-assistant-elgato-lighting/spec.md` and
`specs/home-assistant-elgato-lighting/plan.md`
**Risk Tier**: tiny
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

## Phase 2: Implementation

- [x] T004 [FR-001] [FR-002] Add Elgato discovery and manual setup guidance to
      `docs/runbooks/home-assistant.md`.
- [x] T005 [FR-003] [FR-004] Add Elgato entity inventory and runtime-state
      safety guidance to `docs/runbooks/home-assistant.md`.
- [x] T006 [FR-005] Re-check constitution gates after implementation edits.

## Phase 3: Verification

- [x] T007 [FR-TEST] Run
      `kubectl kustomize kubernetes/apps/home-assistant`.
- [x] T008 [FR-TEST] Run
      `kubectl kustomize kubernetes/apps/home-assistant/branch`.
- [x] T009 [FR-SMOKE] Record docs-only development smoke exception.
- [x] T010 [FR-EVIDENCE] Record command outcomes, smoke evidence, exceptions,
      and final `HEAD` in `specs/home-assistant-elgato-lighting/evidence.md`.

## Phase 4: Commit And PR

- [x] T011 [FR-PR] Commit with a conventional commit message.
- [ ] T012 [FR-PR] Push branch `codex/home-assistant-elgato-lighting` and open
      a PR after separate verifier approval.
