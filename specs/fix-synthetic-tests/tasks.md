# Tasks: fix-synthetic-tests

**Input**: `specs/fix-synthetic-tests/spec.md` and
`specs/fix-synthetic-tests/plan.md`
**Risk Tier**: low
**Prerequisites**: Branch `codex/fix-synthetic-tests` and matching
`specs/fix-synthetic-tests/` artifacts. `spec.md` and `plan.md` are approved
inputs to this task list, not implementation tasks.

## Human Gate Status

**Spec Gate**: approved by user request and follow-up correction.

**Plan Gate**: approved by user request.

**Analyze Requirement**: skipped; focused low-risk repair with direct failing checks, recorded in evidence.

## Format: `[ID] [P?] [Req] Description`

- **[P]**: Can run in parallel or fan out to a helper lane because it touches
  different files or performs read-only validation and has no dependency on
  another incomplete task.
- **[Req]**: Requirement or user story trace, such as `FR-001` or `US1`.
- Include exact file paths in each task.
- Keep fanout coordinated through this task list and consolidate all results
  into `specs/fix-synthetic-tests/evidence.md`.

## Phase 1: Setup

- [x] T001 [FR-SETUP] Confirm branch, approved spec/plan, and documentation expectations in `specs/fix-synthetic-tests/`.
- [x] T002 [FR-SETUP] Install or verify local Node dependencies in `tests/smoke/`.

## Phase 2: Implementation

- [x] T003 [FR-001] Reproduce and identify the failing root-domain Homepage smoke behavior in `tests/smoke/routes.spec.js`.
- [x] T004 [FR-001] Retarget Homepage smoke to `homepage.${cluster_domain}` in `tests/smoke/routes.spec.js`.
- [x] T005 [FR-002] Mirror the Homepage smoke target in `kubernetes/apps/synthetics/smoke/routes.spec.js`.
- [x] T006 [FR-003] Re-check synthetic summary helper behavior in `kubernetes/apps/synthetics/smoke/`.
- [x] T007 [FR-DOCS] Update stale route target docs in `docs/runbooks/synthetic-smoke-tests.md` and `kubernetes/apps/homepage/README.md`.

## Phase 3: Verification

- [x] T008 [FR-TEST] Run `python3 tools/policy/check_synthetic_smoke_mirroring.py`.
- [x] T009 [P] [FR-TEST] Run `python3 -m unittest tools.policy.tests.test_check_synthetic_smoke_mirroring`.
- [x] T010 [P] [FR-TEST] Run `node --test kubernetes/apps/synthetics/smoke/*.test.js`.
- [x] T011 [FR-TEST] Run `npm test -- --reporter=list` from `tests/smoke/`.
- [x] T012 [FR-TEST] Run `python3 tools/architecture/render.py --check`.
- [x] T013 [FR-SMOKE] Record no-development-smoke rationale in `specs/fix-synthetic-tests/evidence.md`.
- [x] T014 [FR-CONVERGE] Record skipped-converge rationale in `specs/fix-synthetic-tests/evidence.md`.
- [x] T015 [FR-EVIDENCE] Record command outcomes and final state in `specs/fix-synthetic-tests/evidence.md`.

## Phase 4: Commit And PR

- [ ] T016 [FR-PR] Amend commit with a conventional commit message.
- [ ] T017 [FR-PR] Force-push branch `codex/fix-synthetic-tests` and update PR #367.

## Dependencies

T001-T003 must complete before implementation edits. T008-T012 run after T004-T007.

## Parallel Execution Examples

After edits, T009 and T010 can run independently while T008 checks mirror state.

## Implementation Strategy

Fix the single failing smoke path first, then run mirrored policy and full Playwright smoke before updating the PR branch.
