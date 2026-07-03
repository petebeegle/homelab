---
description: "Homelab SDD task list for workflow guard hardening"
---

# Tasks: sdd-workflow-guards

**Input**: `specs/sdd-workflow-guards/spec.md` and
`specs/sdd-workflow-guards/plan.md`
**Risk Tier**: low
**Prerequisites**: Valid workflow marker, implementation plan, owner
attestation, and delegation token under `.codex/tmp/`

## Format: `[ID] [P?] [Req] Description`

- **[P]**: Can run in parallel because it touches different files and has no
  dependency on another task.
- **[Req]**: Requirement or user story trace, such as `FR-001` or `US1`.
- Include exact file paths in each task.

## Phase 1: Workflow Setup

- [x] T001 [FR-OWN] Create the sibling clone at
      `/workspaces/homelab-ideas/sdd-workflow-guards` on
      `codex/sdd-workflow-guards`.
- [x] T002 [FR-OWN] Create `.codex/tmp/active-implementation`,
      `.codex/tmp/implementation-plan.yaml`,
      `.codex/tmp/implementation-owner-attestation.yaml`, and matching
      delegation token evidence.
- [x] T003 [FR-OWN] Run the three owner workflow validators and record outcomes
      in `specs/sdd-workflow-guards/evidence.md`.

## Phase 2: Spec And Plan

- [x] T004 [FR-SPEC] Write `specs/sdd-workflow-guards/spec.md`.
- [x] T005 [FR-PLAN] Write `specs/sdd-workflow-guards/plan.md`, including
      tiered TDD and development validation expectations.
- [x] T006 [FR-DOCS] Confirm documentation impact and generated architecture
      expectations.

## Phase 3: Implementation

- [x] T007 [P] [FR-001,FR-002] Add SDD context validation under
      `tools/codex-harness/`.
- [x] T008 [P] [FR-001] Wire SDD artifact checks into
      `.codex/hooks/implementation_workflow_guard.sh`.
- [x] T009 [FR-003] Move PR creation gates into
      `.codex/scripts/create_implementation_pr.sh --auto`.
- [x] T010 [FR-004,FR-005] Update `.codex/hooks/verifier_push_guard.sh` for the
      narrow smoke push exception while preserving exact-HEAD gates.
- [x] T011 [FR-006] Add focused tests under `tools/codex-harness/tests/`.
- [x] T012 [FR-DOCS] Update
      `docs/runbooks/spec-driven-development.md` and
      `docs/runbooks/implementation-workflow.md`.
- [x] T013 [FR-IMPL] Re-check constitution gates after implementation edits.

## Phase 4: Verification

- [x] T014 [FR-TEST] Run `python3 -m unittest discover -s
      tools/codex-harness/tests`.
- [x] T015 [FR-TEST] Run `pre-commit run --all-files`.
- [x] T016 [FR-TEST] Run `python3 tools/architecture/render.py --check`.
- [x] T017 [FR-TEST] Run `python3 -m unittest discover -s
      tools/development/tests`.
- [x] T018 [FR-TEST] Run `python3 -m unittest discover -s
      tools/context-pack/tests`.
- [x] T019 [FR-TEST] Run `uv run --project tools/agent-memory pytest
      tools/agent-memory/tests`.
- [x] T020 [FR-TEST] Run `npx -y agnix@0.25.0 .`.
- [x] T021 [FR-SMOKE] Record development smoke exception for local-only
      workflow guard changes.
- [x] T022 [FR-EVIDENCE] Record command outcomes, exceptions, final branch, and
      final `HEAD` in `specs/sdd-workflow-guards/evidence.md`.

## Phase 5: Commit And Handoff

- [x] T023 [FR-PR] Write `.codex/tmp/pr-summary.md` from the plan and final
      evidence.
- [x] T024 [FR-PR] Commit with a conventional commit message.
- [ ] T025 [FR-PR] Report exact `HEAD` and do not create verifier approval or a
      PR.
