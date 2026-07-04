---
description: "Document smoke kube alias usage tasks"
---

# Tasks: document-smoke-kube-aliases

**Input**: `specs/document-smoke-kube-aliases/spec.md` and
`specs/document-smoke-kube-aliases/plan.md`
**Risk Tier**: tiny
**Prerequisites**: Branch `codex/document-smoke-kube-aliases` and matching
`specs/document-smoke-kube-aliases/` artifacts.

## Format: `[ID] [P?] [Req] Description`

- **[P]**: Can run in parallel because it touches different files and has no
  dependency on another task.
- **[Req]**: Requirement or user story trace, such as `FR-001` or `US1`.
- Include exact file paths in each task.

## Phase 1: Spec And Plan

- [x] T001 [FR-SPEC] Create
      `specs/document-smoke-kube-aliases/spec.md`.
- [x] T002 [FR-PLAN] Create
      `specs/document-smoke-kube-aliases/plan.md`, including tiered TDD and
      development validation expectations.
- [x] T003 [FR-DOCS] Confirm documentation impact and generated architecture
      expectations in `specs/document-smoke-kube-aliases/plan.md`.

## Phase 2: Implementation

- [x] T004 [FR-001,FR-002,FR-003] Edit
      `docs/runbooks/synthetic-smoke-tests.md` to document
      `scripts/kube-aliases.sh`, alias targets, context confirmation, and
      production manual smoke commands through `kp`.
- [x] T005 [FR-004] Re-check constitution gates after implementation edits in
      `specs/document-smoke-kube-aliases/plan.md`.

## Phase 3: Verification

- [x] T006 [FR-TEST] Run targeted `rg` validation against
      `docs/runbooks/synthetic-smoke-tests.md`.
- [x] T007 [FR-TEST] Run `python3 tools/architecture/render.py --check`.
- [x] T008 [FR-TEST] Run
      `python3 tools/codex-harness/validate_sdd_context.py --root "$(pwd)" --branch "$(git branch --show-current)" --require-plan-artifacts`.
- [x] T009 [FR-SMOKE] Record docs-only development smoke exception in
      `specs/document-smoke-kube-aliases/evidence.md`.
- [x] T010 [FR-EVIDENCE] Record command outcomes, exceptions, and final `HEAD`
      in `specs/document-smoke-kube-aliases/evidence.md`.

## Phase 4: Commit And PR

- [x] T011 [FR-PR] Commit with a conventional commit message.
- [x] T012 [FR-PR] Leave branch ready for push and PR creation.
