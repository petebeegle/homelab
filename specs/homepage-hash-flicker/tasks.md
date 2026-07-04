# Tasks: Homepage Hash Flicker

**Input**: `specs/homepage-hash-flicker/spec.md` and
`specs/homepage-hash-flicker/plan.md`
**Risk Tier**: medium
**Prerequisites**: Branch `codex/homepage-hash-flicker` and matching
`specs/homepage-hash-flicker/` artifacts.

## Format: `[ID] [P?] [Req] Description`

- **[P]**: Can run in parallel or fan out to a helper lane because it touches
  different files or performs read-only validation and has no dependency on
  another incomplete task.
- **[Req]**: Requirement or user story trace, such as `FR-001` or `US1`.
- Include exact file paths in each task.
- Keep fanout coordinated through this task list and consolidate all results
  into `specs/homepage-hash-flicker/evidence.md`.

## Phase 1: Spec And Plan

- [X] T001 [FR-SPEC] Create `specs/homepage-hash-flicker/spec.md`.
- [X] T002 [FR-PLAN] Create `specs/homepage-hash-flicker/plan.md`,
      including tiered TDD and development validation expectations.
- [X] T003 [FR-DOCS] Confirm documentation impact and generated architecture
      expectations in `specs/homepage-hash-flicker/plan.md`.

## Phase 2: Implementation

- [X] T004 [FR-001] Edit `kubernetes/apps/homepage/base/deployment.yaml` so
      the shared Homepage Deployment uses `replicas: 1`.
- [X] T005 [FR-002] Verify the branch Homepage manifest, Service, HTTPRoute,
      PDB, and config merge behavior are not changed.
- [X] T006 [FR-002] Re-check constitution gates after implementation edits in
      `specs/homepage-hash-flicker/plan.md`.

## Phase 3: Verification

- [X] T007 [FR-004] Render production Homepage with strict envsubst and assert
      `Deployment/homepage` has `replicas: 1`.
- [X] T008 [FR-004] Render development Homepage with strict envsubst and assert
      `Deployment/homepage` has `replicas: 1`.
- [ ] T009 [FR-005] Run Homepage development smoke validation or record the
      unavailable-infrastructure exception in
      `specs/homepage-hash-flicker/evidence.md`.
- [ ] T010 [FR-003] Record command outcomes, URLs, smoke evidence, skipped
      checks, exceptions, and final branch state in
      `specs/homepage-hash-flicker/evidence.md`.

## Phase 4: Commit And PR

- [ ] T011 [FR-PR] Commit with a conventional commit message.
- [ ] T012 [FR-PR] Push branch `codex/homepage-hash-flicker` and open a PR.

## Dependencies

- T004 depends on T001-T003.
- T007 and T008 depend on T004.
- T009 depends on T004 and can run after local render checks.
- T010 depends on all completed implementation and verification tasks.
- T011 and T012 are intentionally left for PR publication flow.

## Fanout Guidance

- T007 and T008 are read-only render checks and may run independently.
- Live read-only curl checks may run independently from render checks.
- Tracked edits stay sequential because this implementation changes a single
  manifest and one artifact set.
