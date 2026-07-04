---
description: "Homelab SDD task list template"
---

# Tasks: [IMPLEMENTATION]

**Input**: `specs/[IMPLEMENTATION]/spec.md` and
`specs/[IMPLEMENTATION]/plan.md`
**Risk Tier**: [tiny|low|medium|high]
**Prerequisites**: Branch `codex/[IMPLEMENTATION]` and matching
`specs/[IMPLEMENTATION]/` artifacts.

## Format: `[ID] [P?] [Req] Description`

- **[P]**: Can run in parallel because it touches different files and has no
  dependency on another task.
- **[Req]**: Requirement or user story trace, such as `FR-001` or `US1`.
- Include exact file paths in each task.

## Phase 1: Spec And Plan

- [ ] T001 [FR-SPEC] Create or update `specs/[IMPLEMENTATION]/spec.md`.
- [ ] T002 [FR-PLAN] Create or update `specs/[IMPLEMENTATION]/plan.md`,
      including tiered TDD and development validation expectations.
- [ ] T003 [FR-DOCS] Confirm documentation impact and generated architecture
      expectations.

## Phase 2: Implementation

- [ ] T004 [P] [FR-IMPL] Edit [path].
- [ ] T005 [P] [FR-IMPL] Edit [path].
- [ ] T006 [FR-IMPL] Re-check constitution gates after implementation edits.

## Phase 3: Verification

- [ ] T007 [FR-TEST] Run [focused local command].
- [ ] T008 [FR-TEST] Run [broader local command].
- [ ] T009 [FR-SMOKE] Run development smoke validation or record why the tier
      does not require it.
- [ ] T010 [FR-EVIDENCE] Record command outcomes, smoke evidence, exceptions,
      and final `HEAD` in `specs/[IMPLEMENTATION]/evidence.md`.

## Phase 4: Commit And PR

- [ ] T011 [FR-PR] Commit with a conventional commit message.
- [ ] T012 [FR-PR] Push branch `codex/[IMPLEMENTATION]` and open a PR.

## Tier Guidance

**Tiny**

- Keep tasks minimal.
- Evidence may be review-only plus a focused validator when available.

**Low**

- Include relevant local checks.
- Add or update a small test when touching executable code and a test seam
  exists.

**Medium**

- Include focused render/unit tests for changed manifests or tools.
- Include development-cluster validation for covered cluster-affecting changes,
  or a documented unavailable-infrastructure exception.

**High**

- Include broad local checks and development validation for affected apps or
  shared base paths.
- Use `--include-cluster-base` when shared development base resources must
  reconcile before app acceptance.
