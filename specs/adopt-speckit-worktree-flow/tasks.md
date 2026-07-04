# Tasks: adopt-speckit-worktree-flow

**Input**: `specs/adopt-speckit-worktree-flow/spec.md` and
`specs/adopt-speckit-worktree-flow/plan.md`
**Risk Tier**: medium

## Phase 1: Guidance And Templates

- [x] T001 [FR-001] Update `AGENTS.md` to name Spec Kit plus default worktree
      isolation as the repository implementation flow.
- [x] T002 [FR-001] Update `.specify/memory/constitution.md` to remove local
      attestation requirements.
- [x] T003 [FR-007] Update `.specify/templates/spec-template.md`,
      `.specify/templates/plan-template.md`,
      `.specify/templates/tasks-template.md`, and
      `.specify/templates/evidence-template.md`.
- [x] T004 [FR-001] Update `docs/runbooks/spec-driven-development.md`,
      `docs/runbooks/implementation-workflow.md`, and
      `docs/runbooks/codex-workflow-protocol.md`.
- [x] T005 [FR-001] Update
      `docs/decisions/codex-implementation-workflow.md` and
      `docs/decisions/tdd-and-development-smoke-evidence.md`.

## Phase 2: Guards And Automation

- [x] T006 [FR-002] Update `.codex/hooks/user_prompt_submit.sh` to recommend
      default worktree mode.
- [x] T007 [FR-003] [FR-004] [FR-005] Simplify
      `.codex/hooks/implementation_workflow_guard.sh` to enforce branch and SDD
      artifact invariants.
- [x] T008 [FR-006] Simplify `.codex/hooks/verifier_push_guard.sh` into a
      branch/evidence push guard.
- [x] T009 [FR-006] Simplify `.codex/scripts/create_implementation_pr.sh` to
      require valid SDD evidence instead of verifier files.

## Phase 3: Tests

- [x] T010 [FR-002] Update user prompt hook tests for default worktree guidance.
- [x] T011 [FR-003] [FR-004] [FR-005] Update workflow guard tests for branch and
      artifact enforcement.
- [x] T012 [FR-006] Update push and PR automation tests to remove verifier file
      requirements.

## Phase 4: Verification

- [x] T013 [FR-TEST] Run focused Codex harness tests.
- [x] T014 [FR-TEST] Run `python3 tools/architecture/render.py --check`.
- [x] T015 [FR-TEST] Run `pre-commit run --all-files` if practical.
- [x] T016 [FR-EVIDENCE] Record outcomes and final state in
      `specs/adopt-speckit-worktree-flow/evidence.md`.
