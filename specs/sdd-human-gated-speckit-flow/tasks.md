---
description: "Repair Homelab SDD human gate workflow"
---

# Tasks: sdd-human-gated-speckit-flow

**Input**: `specs/sdd-human-gated-speckit-flow/spec.md` and
`specs/sdd-human-gated-speckit-flow/plan.md`
**Risk Tier**: low
**Prerequisites**: Branch `codex/sdd-human-gated-speckit-flow`, matching
`specs/sdd-human-gated-speckit-flow/` artifacts, and user-approved plan.

## Format: `[ID] [P?] [Req] Description`

- **[P]**: Can run in parallel or fan out because it touches different files or
  performs read-only validation and has no dependency on another incomplete
  task.
- **[Req]**: Requirement or user story trace, such as `FR-001` or `US1`.
- Include exact file paths in each task.
- Consolidate results into
  `specs/sdd-human-gated-speckit-flow/evidence.md`.

## Phase 1: Documentation Contract

- [X] T001 [FR-001,FR-002,US1] Update
      `docs/runbooks/spec-driven-development.md` with human decision workflow,
      gate sequence, lightweight exceptions, and upstream conformance guidance.
- [X] T002 [FR-001,FR-002,US1] Update
      `docs/runbooks/implementation-workflow.md` with the normal meaningful-work
      SDD path and evidence expectations.
- [X] T003 [FR-001,US1] Update `AGENTS.md` with concise human-gate guidance.

## Phase 2: Templates And Workflow

- [X] T004 [FR-004,US1,US2] Update
      `.specify/templates/spec-template.md`,
      `.specify/templates/plan-template.md`, and
      `.specify/templates/evidence-template.md` with human gate and skipped-gate
      evidence fields.
- [X] T005 [FR-005,US3] Update `.specify/templates/tasks-template.md` so spec
      and plan are prerequisites, not implementation tasks.
- [X] T006 [FR-006,US1] Update `.specify/workflows/speckit/workflow.yml` with
      clarify, checklist, analyze, implement, converge, and review gates.

## Phase 3: Verification

- [X] T007 [P] [FR-007] Run
      `python3 tools/codex-harness/validate_sdd_context.py --root "$(pwd)" --branch "$(git branch --show-current)" --require-plan-artifacts`.
- [X] T008 [P] [FR-007] Run `python3 tools/architecture/render.py --check`.
- [X] T009 [P] [FR-007] Run `git diff --check`.
- [X] T010 [P] [FR-007] Run targeted `rg` checks for `clarify`, `checklist`,
      `analyze`, `converge`, `human gate`, and absence of `Spec And Plan` in
      `.specify/templates/tasks-template.md`.
- [X] T011 [FR-007] Manually inspect `.specify/workflows/speckit/workflow.yml`
      order against upstream Spec Kit quickstart.

## Phase 4: Evidence And Handoff

- [X] T012 [FR-007] Record command outcomes, skipped gate exceptions, docs-only
      smoke exception, upstream conformance review, final branch, and final
      `HEAD` in `specs/sdd-human-gated-speckit-flow/evidence.md`.
- [X] T013 [FR-007] Review `git diff --stat` and `git status --short`.
