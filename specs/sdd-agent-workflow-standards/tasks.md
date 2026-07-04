---
description: "General SDD-first agent workflow implementation tasks"
---

# Tasks: sdd-agent-workflow-standards

**Input**: `specs/sdd-agent-workflow-standards/spec.md` and
`specs/sdd-agent-workflow-standards/plan.md`
**Risk Tier**: low
**Prerequisites**: Branch `codex/sdd-agent-workflow-standards` and matching
`specs/sdd-agent-workflow-standards/` artifacts.

## Format: `[ID] [P?] [Req] Description`

- **[P]**: Can run in parallel because it touches different files and has no
  dependency on another task.
- **[Req]**: Requirement or user story trace, such as `FR-001` or `US1`.
- Include exact file paths in each task.

## Phase 1: Spec And Plan

- [X] T001 [FR-SPEC] Create
      `specs/sdd-agent-workflow-standards/spec.md`.
- [X] T002 [FR-PLAN] Create
      `specs/sdd-agent-workflow-standards/plan.md`, including SDD tier,
      workflow tier, smoke strategy, fanout targets, and exceptions.
- [X] T003 [FR-DOCS] Confirm documentation impact and generated architecture
      expectations in `specs/sdd-agent-workflow-standards/plan.md`.

## Phase 2: Implementation

- [X] T004 [P] [FR-001,FR-005,FR-006] Update
      `docs/runbooks/spec-driven-development.md` with SDD-first, smoke-first,
      fanout, and upstream conformance guidance.
- [X] T005 [P] [FR-001,FR-005,FR-006] Update
      `docs/runbooks/implementation-workflow.md` with exact completion states,
      automated smoke preference, fanout defaults, and post-merge verification.
- [X] T006 [P] [FR-002,FR-003,FR-004] Update `.specify/templates/plan-template.md`,
      `.specify/templates/tasks-template.md`, and
      `.specify/templates/evidence-template.md`.
- [X] T007 [P] [FR-001] Update `AGENTS.md` with concise smoke/fanout workflow
      reminders.
- [X] T008 [FR-IMPL] Re-check constitution gates after implementation edits in
      `specs/sdd-agent-workflow-standards/plan.md`.

## Phase 3: Verification

- [X] T009 [FR-TEST] Run
      `python3 tools/codex-harness/validate_sdd_context.py --root "$(pwd)" --branch "$(git branch --show-current)" --require-plan-artifacts`.
- [X] T010 [FR-TEST] Run `python3 tools/architecture/render.py --check`.
- [X] T011 [FR-TEST] Run `git diff --check`.
- [X] T012 [FR-TEST] Run targeted `rg` checks for smoke, fanout, upstream
      conformance, and completion-state language.
- [X] T013 [FR-SMOKE] Record development smoke profile `none` with docs-only
      rationale in `specs/sdd-agent-workflow-standards/evidence.md`.
- [X] T014 [FR-EVIDENCE] Record upstream Spec Kit conformance review,
      command outcomes, exceptions, and final `HEAD` in
      `specs/sdd-agent-workflow-standards/evidence.md`.

## Phase 4: Commit And PR

- [X] T015 [FR-PR] Commit with a conventional commit message.
- [X] T016 [FR-PR] Push branch `codex/sdd-agent-workflow-standards` and open a
      PR.

## Fanout Notes

- T004-T007 are safe fanout targets because they touch separate files or
  template groups and can be reviewed against the same requirements.
- T009-T012 are safe fanout targets after implementation edits because they are
  read-only validation commands.
- T014 consolidates all fanout results into one evidence file.
