# Tasks: sdd-synthetic-smoke-mirroring

**Input**: `specs/sdd-synthetic-smoke-mirroring/spec.md` and
`specs/sdd-synthetic-smoke-mirroring/plan.md`
**Risk Tier**: low
**Prerequisites**: Valid workflow marker, implementation plan, owner
attestation, and delegation token under `.codex/tmp/`

## Format: `[ID] [P?] [Req] Description`

- **[P]**: Can run in parallel because it touches different files and has no
  dependency on another task.
- **[Req]**: Requirement or user story trace, such as `FR-001` or `US1`.
- Include exact file paths in each task.

## Phase 1: Workflow Setup

- [x] T001 [FR-OWN] Create or refresh the sibling clone at
      `/workspaces/homelab-ideas/sdd-synthetic-smoke-mirroring` on
      `codex/sdd-synthetic-smoke-mirroring`.
- [x] T002 [FR-OWN] Create `.codex/tmp/active-implementation`,
      `.codex/tmp/implementation-plan.yaml`,
      `.codex/tmp/implementation-owner-attestation.yaml`, and
      `.codex/tmp/delegation-tokens/implementation-agent-sdd-synthetic-smoke-mirroring.token`.
- [x] T003 [FR-OWN] Run the three owner workflow validators and record outcomes
      in `specs/sdd-synthetic-smoke-mirroring/evidence.md`.

## Phase 2: Spec And Plan

- [x] T004 [FR-SPEC] Write
      `specs/sdd-synthetic-smoke-mirroring/spec.md`.
- [x] T005 [FR-PLAN] Write
      `specs/sdd-synthetic-smoke-mirroring/plan.md`, including tiered TDD and
      development validation expectations.
- [x] T006 [FR-DOCS] Confirm documentation impact and generated architecture
      expectations in `specs/sdd-synthetic-smoke-mirroring/plan.md`.

## Phase 3: Implementation

- [x] T007 [FR-001] [FR-002] Sync the Home Assistant onboarding/OIDC diagnostic
      into `tests/smoke/routes.spec.js` so it mirrors
      `kubernetes/apps/synthetics/smoke/routes.spec.js`.
- [x] T008 [FR-003] [FR-004] [FR-005] Add
      `tools/policy/check_synthetic_smoke_mirroring.py` to compare only required
      mirrored smoke file pairs.
- [x] T009 [FR-007] Add focused tests in
      `tools/policy/tests/test_check_synthetic_smoke_mirroring.py`.
- [x] T010 [FR-006] Wire the mirror policy check into
      `.pre-commit-config.yaml` for relevant mirrored smoke files.
- [x] T011 [FR-008] Update `docs/runbooks/synthetic-smoke-tests.md` with the
      enforced mirror rule and intentional exclusions.
- [x] T012 [FR-PLAN] Re-check constitution gates after implementation edits in
      `specs/sdd-synthetic-smoke-mirroring/plan.md`.

## Phase 4: Verification

- [x] T013 [FR-009] Run `python3 -m unittest discover -s tools/policy/tests`.
- [x] T014 [FR-009] Run
      `python3 -m unittest discover -s tools/development/tests`.
- [x] T015 [FR-009] Run
      `python3 -m unittest discover -s tools/codex-harness/tests`.
- [x] T016 [FR-009] Run
      `python3 -m unittest discover -s tools/context-pack/tests`.
- [x] T017 [FR-009] Run `pre-commit run --all-files`.
- [x] T018 [FR-009] Run `python3 tools/architecture/render.py --check`.
- [x] T019 [FR-009] Run `npx -y agnix@0.25.0 .`.
- [x] T020 [FR-009] Run `npm ci && npm test` in `tests/smoke` and clean
      generated output.
- [x] T021 [FR-009] Run `npm ci && npm test && npm run test:unit` in
      `kubernetes/apps/synthetics/smoke` if practical and clean generated
      output.
- [x] T022 [FR-009] Run
      `uv run --project tools/agent-memory pytest tools/agent-memory/tests` or
      record the Python 3.14.6 environment limitation if it persists.
- [ ] T023 [FR-009] Run the SDD context validator with
      `--require-evidence --head` after commit.
- [ ] T024 [FR-009] Record command outcomes, exceptions, final `HEAD`, and
      documentation impact in `specs/sdd-synthetic-smoke-mirroring/evidence.md`.

## Phase 5: Commit And Handoff

- [ ] T025 [FR-009] Write `.codex/tmp/pr-summary.md` from the plan and final
      evidence.
- [ ] T026 [FR-009] Commit with a conventional commit message.
- [ ] T027 [FR-009] Report exact `HEAD` and do not create verifier approval.

## Dependencies

- Phase 1 must complete before tracked edits.
- Phase 2 bootstraps the durable SDD context before implementation edits.
- T007 must complete before the policy command can pass.
- T008 should complete before T009 and T010.
- Verification tasks run after implementation and documentation edits.
- Final SDD evidence and PR summary are updated after validation and commit.

## Parallel Execution Examples

- T008 and T011 can proceed in parallel after T007 if coordinated carefully
  because they touch different files.
- T014, T015, T016, T018, and T019 can run independently once implementation
  files are stable.

## Implementation Strategy

Deliver the route parity and policy check first, then wire the check into
pre-commit and documentation. Keep validation local and focused because the
change does not alter production route behavior or live cluster desired state.
