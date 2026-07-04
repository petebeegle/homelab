# Tasks: fix-immich-cnpg-scrape

**Input**: `specs/fix-immich-cnpg-scrape/spec.md` and
`specs/fix-immich-cnpg-scrape/plan.md`
**Risk Tier**: high
**Prerequisites**: Branch `codex/fix-immich-cnpg-scrape` and matching
`specs/fix-immich-cnpg-scrape/` artifacts.

## Format: `[ID] [P?] [Req] Description`

- **[P]**: Can run in parallel or fan out to a helper lane because it touches
  different files or performs read-only validation and has no dependency on
  another incomplete task.
- **[Req]**: Requirement or user story trace, such as `FR-001` or `US1`.

## Phase 1: Spec And Plan

- [x] T001 [FR-SPEC] Create `specs/fix-immich-cnpg-scrape/spec.md`.
- [x] T002 [FR-PLAN] Create `specs/fix-immich-cnpg-scrape/plan.md`,
      including tiered TDD and development validation expectations.
- [x] T003 [FR-DOCS] Confirm documentation impact and generated architecture
      expectations.

## Phase 2: Implementation

- [x] T004 [FR-001] Drop CloudNativePG-generated Services from Alloy service
      discovery in `kubernetes/infra/monitoring/alloy/config/config.alloy`.
- [x] T005 [FR-002] Re-check constitution gates after implementation edits.

## Phase 3: Verification

- [x] T006 [P] [FR-004] Run `kubectl kustomize kubernetes/infra/monitoring/alloy`.
- [x] T007 [P] [FR-003] Run Immich Helm template validation with local values.
- [x] T008 [P] [FR-004] Run `kubectl kustomize kubernetes/clusters/production`.
- [x] T009 [FR-004] Record development validation exception and substitute live
      read-only production query evidence.
- [x] T010 [FR-004] Record command outcomes, skipped checks, exceptions, final
      live verification, and final `HEAD` in
      `specs/fix-immich-cnpg-scrape/evidence.md`.

## Phase 4: Commit And PR

- [ ] T011 [FR-PR] Commit with a conventional commit message.
- [ ] T012 [FR-PR] Push branch `codex/fix-immich-cnpg-scrape` and open a PR.
