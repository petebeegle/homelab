---
description: "Development smoke secret staging tasks"
---

# Tasks: dev-secret-staging-for-smoke

## Phase 1: Workflow Setup

- [x] T001 Create the sibling clone on `codex/dev-secret-staging-for-smoke`.
- [x] T002 Create workflow marker, implementation plan, owner attestation, and
      delegation token evidence under `.codex/tmp/`.
- [x] T003 Run owner workflow validators.
- [x] T004 Create `specs/dev-secret-staging-for-smoke/spec.md`,
      `plan.md`, `tasks.md`, and `evidence.md`.

## Phase 2: Tests And Implementation

- [x] T005 Add wrapper unit tests in
      `tools/codex-harness/tests/test_prepare_development_smoke_secrets.py`.
- [x] T006 Add `.codex/scripts/prepare_development_smoke_secrets.sh`.
- [x] T007 Update `docs/runbooks/implementation-workflow.md`,
      `docs/runbooks/development-cluster.md`, and `tools/development/README.md`.

## Phase 3: Verification

- [x] T008 Run focused wrapper tests.
- [x] T009 Run `python3 -m unittest discover -s tools/codex-harness/tests`.
- [x] T010 Run `bash -n .codex/scripts/*.sh`.
- [x] T011 Run `pre-commit run --all-files`.
- [x] T012 Record evidence, final state, and PR summary.
- [x] T013 Commit and hand off for verifier approval.
