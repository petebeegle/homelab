---
description: "Post-migration SDD audit and cleanup tasks"
---

# Tasks: sdd-post-migration-audit

**Input**: `specs/sdd-post-migration-audit/spec.md` and
`specs/sdd-post-migration-audit/plan.md`
**Risk Tier**: tiny
**Prerequisites**: Valid workflow marker, implementation plan, owner
attestation, and delegation token under `.codex/tmp/`

## Format: `[ID] [P?] [Req] Description`

- **[P]**: Can run in parallel because it touches different files and has no
  dependency on another task.
- **[Req]**: Requirement or user story trace, such as `FR-001` or `US1`.
- Include exact file paths in each task.

## Phase 1: Workflow Setup

- [x] T001 [FR-OWN] Create or refresh the sibling clone on
      `codex/sdd-post-migration-audit`.
- [x] T002 [FR-OWN] Create `.codex/tmp/active-implementation`,
      `.codex/tmp/implementation-plan.yaml`,
      `.codex/tmp/implementation-owner-attestation.yaml`, and matching
      delegation token evidence.
- [x] T003 [FR-OWN] Run the three owner workflow validators and record outcomes
      in `specs/sdd-post-migration-audit/evidence.md`.

## Phase 2: Spec And Plan

- [x] T004 [FR-SPEC] Write `specs/sdd-post-migration-audit/spec.md`.
- [x] T005 [FR-PLAN] Write `specs/sdd-post-migration-audit/plan.md`,
      including tiered TDD and development validation expectations.
- [x] T006 [FR-DOCS] Confirm documentation impact and generated architecture
      expectations.

## Phase 3: Audit And Implementation

- [x] T007 [P] [FR-003] Create
      `specs/sdd-post-migration-audit/audit-report.md` with Spec Kit routing,
      open PR classification, backlog, and ignored residue categories.
- [x] T008 [P] [FR-004] Delete duplicated
      `.codex/memory/approved/*.md` guidance and remove
      `.codex/memory/approved/**/*.md` from `.codex/retrieval.yaml`.
- [x] T009 [P] [FR-005] Rewrite `.codex/agents/*.toml` as short pointers to
      canonical docs.
- [x] T010 [P] [FR-006] Prune `.codex/runbooks/README.md` legacy placement
      guidance when no longer useful.
- [x] T011 [P] [FR-006] Keep `tools/development/README.md` as CLI usage docs
      and defer authority to `docs/runbooks/development-cluster.md`.
- [x] T012 [FR-001] Re-check constitution gates after implementation edits.

## Phase 4: Verification

- [x] T013 [FR-TEST] Run
      `python3 tools/policy/check_retrieval_manifest.py`.
- [x] T014 [FR-TEST] Run `python3 tools/architecture/render.py --check`.
- [x] T015 [FR-TEST] Run targeted `rg` checks for stale approved memory
      retrieval and obsolete canonical guidance.
- [x] T016 [FR-TEST] Run `pre-commit run --all-files` if practical.
- [x] T017 [FR-SMOKE] Record docs-only development smoke exception.
- [x] T018 [FR-EVIDENCE] Record command outcomes, smoke evidence, exceptions,
      and final `HEAD` in `specs/sdd-post-migration-audit/evidence.md`.

## Phase 5: Commit And Handoff

- [x] T019 [FR-PR] Write `.codex/tmp/pr-summary.md` from the plan and final
      evidence.
- [x] T020 [FR-PR] Commit with a conventional commit message.
- [x] T021 [FR-PR] Report exact `HEAD` and do not create verifier approval.
