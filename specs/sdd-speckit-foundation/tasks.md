# Tasks: sdd-speckit-foundation

**Input**: `specs/sdd-speckit-foundation/spec.md` and
`specs/sdd-speckit-foundation/plan.md`
**Risk Tier**: low
**Workflow Tier**: docs-only

## Phase 1: Workflow Setup

- [x] T001 [FR-OWN] Clone `https://github.com/petebeegle/homelab.git` into
      `/workspaces/homelab-ideas/sdd-speckit-foundation`.
- [x] T002 [FR-OWN] Create branch `codex/sdd-speckit-foundation` from
      `origin/main`.
- [x] T003 [FR-OWN] Create `.codex/tmp/active-implementation`,
      `.codex/tmp/implementation-plan.yaml`,
      `.codex/tmp/implementation-owner-attestation.yaml`, and matching
      delegation token evidence.
- [x] T004 [FR-OWN] Validate active marker, implementation plan, and owner
      attestation before tracked edits.

## Phase 2: Spec Kit Initialization

- [x] T005 [FR-001] Run Spec Kit initialization with Codex integration.
- [x] T006 [FR-001] Record Spec Kit version and integration outcome in
      `specs/sdd-speckit-foundation/evidence.md`.

## Phase 3: Homelab SDD Guidance

- [x] T007 [FR-002] Replace `.specify/memory/constitution.md` with Homelab
      principles and binding source links.
- [x] T008 [FR-003] Customize `.specify/templates/spec-template.md`.
- [x] T009 [FR-003] Customize `.specify/templates/plan-template.md`.
- [x] T010 [FR-003] Customize `.specify/templates/tasks-template.md`.
- [x] T011 [FR-003] Add `.specify/templates/evidence-template.md`.
- [x] T012 [FR-004] Add `docs/runbooks/spec-driven-development.md`.
- [x] T013 [FR-005] Shorten `AGENTS.md` into an SDD and canonical-authority
      router.
- [x] T014 [FR-006] Add `specs/sdd-speckit-foundation/spec.md`.
- [x] T015 [FR-006] Add `specs/sdd-speckit-foundation/plan.md`.
- [x] T016 [FR-006] Add `specs/sdd-speckit-foundation/tasks.md`.
- [x] T017 [FR-006] Add initial `specs/sdd-speckit-foundation/evidence.md`.

## Phase 4: Verification

- [x] T018 [FR-007] Run `pre-commit run --all-files`.
- [x] T019 [FR-007] Run `python3 tools/architecture/render.py --check`.
- [x] T020 [FR-007] Run
      `python3 -m unittest discover -s tools/codex-harness/tests`.
- [x] T021 [FR-007] Run
      `python3 -m unittest discover -s tools/development/tests`.
- [x] T022 [FR-007] Run
      `python3 -m unittest discover -s tools/context-pack/tests`.
- [x] T023 [FR-007] Run
      `uv run --project tools/agent-memory pytest tools/agent-memory/tests`.
- [x] T024 [FR-007] Run `npm ci && npm test` in `tests/smoke`.
- [x] T025 [FR-007] Record all command outcomes and exceptions in
      `specs/sdd-speckit-foundation/evidence.md`.

## Phase 5: Commit And Handoff

- [x] T026 [FR-007] Write `.codex/tmp/pr-summary.md`.
- [x] T027 [FR-007] Commit with a conventional commit.
- [ ] T028 [FR-007] Report final `HEAD` without creating verifier approval or a
      PR.
