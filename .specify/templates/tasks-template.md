---
description: "Homelab SDD task list template"
---

# Tasks: [IMPLEMENTATION]

**Input**: `specs/[IMPLEMENTATION]/spec.md` and
`specs/[IMPLEMENTATION]/plan.md`
**Risk Tier**: [tiny|low|medium|high]
**Prerequisites**: Valid workflow marker, implementation plan, owner attestation,
and delegation token under `.codex/tmp/`

## Format: `[ID] [P?] [Req] Description`

- **[P]**: Can run in parallel because it touches different files and has no
  dependency on another task.
- **[Req]**: Requirement or user story trace, such as `FR-001` or `US1`.
- Include exact file paths in each task.

## Phase 1: Workflow Setup

- [ ] T001 [FR-OWN] Create or refresh the sibling clone on
      `codex/[IMPLEMENTATION]`.
- [ ] T002 [FR-OWN] Create `.codex/tmp/active-implementation`,
      `.codex/tmp/implementation-plan.yaml`,
      `.codex/tmp/implementation-owner-attestation.yaml`, and matching
      delegation token evidence.
- [ ] T003 [FR-OWN] Run the three owner workflow validators and record outcomes
      in `specs/[IMPLEMENTATION]/evidence.md`.

## Phase 2: Spec And Plan

- [ ] T004 [FR-SPEC] Write or update `specs/[IMPLEMENTATION]/spec.md`.
- [ ] T005 [FR-PLAN] Write or update `specs/[IMPLEMENTATION]/plan.md`,
      including tiered TDD and development validation expectations.
- [ ] T006 [FR-DOCS] Confirm documentation impact and generated architecture
      expectations.

## Phase 3: Implementation

- [ ] T007 [P] [FR-IMPL] Edit [path].
- [ ] T008 [P] [FR-IMPL] Edit [path].
- [ ] T009 [FR-IMPL] Re-check constitution gates after implementation edits.

## Phase 4: Verification

- [ ] T010 [FR-TEST] Run [focused local command].
- [ ] T011 [FR-TEST] Run [broader local command].
- [ ] T012 [FR-SMOKE] Run development smoke validation or record why the tier
      does not require it.
- [ ] T013 [FR-EVIDENCE] Record command outcomes, smoke evidence, exceptions,
      and final `HEAD` in `specs/[IMPLEMENTATION]/evidence.md`.

## Phase 5: Commit And Handoff

- [ ] T014 [FR-PR] Write `.codex/tmp/pr-summary.md` from the plan and final
      evidence.
- [ ] T015 [FR-PR] Commit with a conventional commit message.
- [ ] T016 [FR-PR] Report exact `HEAD` and do not create verifier approval.

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

- Prefer helper lanes where available.
- Include broad local checks and development validation for affected apps or
  shared base paths.
- Use `--include-cluster-base` when shared development base resources must
  reconcile before app acceptance.
