---
description: "Homelab SDD task list template"
---

# Tasks: [IMPLEMENTATION]

**Input**: `specs/[IMPLEMENTATION]/spec.md` and
`specs/[IMPLEMENTATION]/plan.md`
**Risk Tier**: [tiny|low|medium|high]
**Prerequisites**: Branch `codex/[IMPLEMENTATION]` and matching
`specs/[IMPLEMENTATION]/` artifacts. `spec.md` and `plan.md` are approved
inputs to this task list, not implementation tasks.

## Human Gate Status

**Spec Gate**: [approved by <who/context>]

**Plan Gate**: [approved by <who/context>]

**Analyze Requirement**: [run before implementation | skipped with rationale]

## Format: `[ID] [P?] [Req] Description`

- **[P]**: Can run in parallel or fan out to a helper lane because it touches
  different files or performs read-only validation and has no dependency on
  another incomplete task.
- **[Req]**: Requirement or user story trace, such as `FR-001` or `US1`.
- Include exact file paths in each task.
- Keep fanout coordinated through this task list and consolidate all results
  into `specs/[IMPLEMENTATION]/evidence.md`.

## Phase 1: Setup

- [ ] T001 [FR-SETUP] Confirm branch, approved spec/plan, and documentation
      expectations.
- [ ] T002 [FR-SETUP] Prepare any required local fixtures, generated inputs, or
      test harness state.

## Phase 2: Implementation

- [ ] T003 [P] [FR-IMPL] Edit [path].
- [ ] T004 [P] [FR-IMPL] Edit [path].
- [ ] T005 [FR-IMPL] Re-check constitution gates after implementation edits.

## Phase 3: Verification

- [ ] T006 [FR-ANALYZE] Run Spec Kit analyze before implementation, or record
      skipped-analyze rationale in evidence for lightweight work.
- [ ] T007 [FR-TEST] Run [focused local command].
- [ ] T008 [FR-TEST] Run [broader local command].
- [ ] T009 [FR-SMOKE] Run development smoke validation or record why the tier
      does not require it.
- [ ] T010 [FR-CONVERGE] Run Spec Kit converge after implementation, or record
      skipped-converge rationale in evidence.
- [ ] T011 [FR-EVIDENCE] Record command outcomes, human gate status, SHAs, URLs when applicable,
      smoke evidence, skipped checks, exceptions, final live verification, and
      final `HEAD` in `specs/[IMPLEMENTATION]/evidence.md`.

## Phase 4: Commit And PR

- [ ] T012 [FR-PR] Commit with a conventional commit message.
- [ ] T013 [FR-PR] Push branch `codex/[IMPLEMENTATION]` and open a PR.

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

## Fanout Guidance

- Prefer fanout for independent repo inspection, test design, render checks,
  smoke execution, docs/evidence updates, public/private repo audits, and live
  read-only verification.
- Do not fan out tracked edits that touch the same files unless the task
  boundary is explicit enough to avoid conflicts.
- Fanout does not change the one implementation, one branch, one
  `specs/[IMPLEMENTATION]/`, one PR contract.
