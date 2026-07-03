---
description: "Development smoke matrix expansion task list"
---

# Tasks: sdd-dev-smoke-matrix

**Input**: `specs/sdd-dev-smoke-matrix/spec.md` and
`specs/sdd-dev-smoke-matrix/plan.md`
**Risk Tier**: medium
**Prerequisites**: Valid workflow marker, implementation plan, owner attestation,
and delegation token under `.codex/tmp/`

## Format: `[ID] [P?] [Req] Description`

- **[P]**: Can run in parallel because it touches different files and has no
  dependency on another task.
- **[Req]**: Requirement or user story trace, such as `FR-001` or `US1`.
- Include exact file paths in each task.

## Phase 1: Workflow Setup

- [x] T001 [FR-OWN] Create or refresh the sibling clone at
      `/workspaces/homelab-ideas/sdd-dev-smoke-matrix` on
      `codex/sdd-dev-smoke-matrix`.
- [x] T002 [FR-OWN] Create `.codex/tmp/active-implementation`,
      `.codex/tmp/implementation-plan.yaml`,
      `.codex/tmp/implementation-owner-attestation.yaml`, and matching
      `.codex/tmp/delegation-tokens/implementation-agent-sdd-dev-smoke-matrix.token`.
- [x] T003 [FR-OWN] Run owner workflow validators and record outcomes in
      `specs/sdd-dev-smoke-matrix/evidence.md`.

## Phase 2: Spec And Plan

- [x] T004 [FR-SPEC] Write `specs/sdd-dev-smoke-matrix/spec.md`.
- [x] T005 [FR-PLAN] Write `specs/sdd-dev-smoke-matrix/plan.md`, including
      tiered TDD and development validation expectations.
- [x] T006 [FR-DOCS] Confirm documentation impact and generated architecture
      expectations.
- [x] T007 [FR-SPEC] Add
      `specs/sdd-dev-smoke-matrix/checklists/smoke-readiness.md`.

## Phase 3: Investigation And Tests

- [x] T008 [P] [FR-001] Inspect existing devverify code and tests:
      `tools/development/devverify/*.py` and
      `tools/development/tests/test_verify_branch_deploy.py`.
- [x] T009 [P] [FR-007,FR-008] Inspect current app manifests and branch
      overlays for `whoami`, `jellyfin`, `home-assistant`, `pihole`,
      `foundryvtt`, `authentik`, and `monitoring`.
- [x] T010 [P] [FR-009] Audit `tests/smoke` and
      `kubernetes/apps/synthetics/smoke` duplication.
- [x] T011 [FR-002,FR-003,FR-004,FR-005,FR-006] Add or update focused tests in
      `tools/development/tests/test_verify_branch_deploy.py` for new profile
      fields, check construction, cleanup, and command sequencing.

## Phase 4: Implementation

- [x] T012 [FR-002,FR-003,FR-004,FR-005] Update
      `tools/development/devverify/config.py`,
      `tools/development/devverify/profiles.py`, and
      `tools/development/devverify/checks.py` for Kustomization, TLSRoute,
      Secret reference, and route URL support.
- [x] T013 [FR-002,FR-003,FR-004] Update
      `tools/development/devverify/cleanup.py`,
      `tools/development/devverify/flux.py`,
      `tools/development/devverify/workflow.py`, and/or
      `tools/development/devverify/cli.py` only where sequencing or cleanup
      requires it.
- [x] T014 [FR-001,FR-007] Update
      `tools/development/smoke-profiles/*.json` and safe branch overlays under
      `kubernetes/apps/*/branch/*` or `kubernetes/clusters/development/branches/*`.
- [x] T015 [FR-008,FR-009] Document authentik, monitoring, Playwright, and
      synthetic smoke mirroring gaps when not implemented directly.
- [x] T016 [FR-DOCS] Update `docs/runbooks/development-cluster.md` and
      `tools/development/README.md`.
- [x] T017 [FR-PLAN] Re-check constitution gates after implementation edits.

## Phase 5: Verification

- [x] T018 [FR-TEST] Run
      `python3 -m unittest discover -s tools/development/tests`.
- [x] T019 [FR-TEST] Run
      `python3 -m unittest discover -s tools/codex-harness/tests`.
- [x] T020 [FR-TEST] Run
      `python3 -m unittest discover -s tools/context-pack/tests`.
- [x] T021 [FR-TEST] Run `pre-commit run --all-files`.
- [x] T022 [FR-TEST] Run `python3 tools/architecture/render.py --check`; run
      `--write` first if Kubernetes/Terraform changes require generated docs.
- [x] T023 [FR-TEST] Run `npx -y agnix@0.25.0 .`.
- [x] T024 [FR-TEST] Run `npm ci && npm test` in `tests/smoke` if touched or
      quick.
- [x] T025 [FR-TEST] Run
      `uv run --project tools/agent-memory pytest tools/agent-memory/tests` or
      record any unrelated Python version limitation.
- [x] T026 [FR-SMOKE] Attempt the whoami development smoke command when
      credentials are available and safe, or record the exception.
- [x] T027 [FR-EVIDENCE] Run SDD context validator with evidence and final
      `HEAD` after commit.
- [x] T028 [FR-EVIDENCE] Record command outcomes, smoke evidence, exceptions,
      and final `HEAD` in `specs/sdd-dev-smoke-matrix/evidence.md`.

## Phase 6: Commit And Handoff

- [x] T029 [FR-PR] Write `.codex/tmp/pr-summary.md` from the plan and final
      evidence.
- [x] T030 [FR-PR] Commit with a conventional commit message.
- [x] T031 [FR-PR] Report exact `HEAD` and do not create verifier approval.
