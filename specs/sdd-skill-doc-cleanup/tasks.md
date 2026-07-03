---
description: "Homelab SDD task list for stale agent docs/config cleanup"
---

# Tasks: sdd-skill-doc-cleanup

**Input**: `specs/sdd-skill-doc-cleanup/spec.md` and
`specs/sdd-skill-doc-cleanup/plan.md`
**Risk Tier**: low
**Prerequisites**: Valid workflow marker, implementation plan, owner attestation,
and delegation token under `.codex/tmp/`

## Format: `[ID] [P?] [Req] Description`

- **[P]**: Can run in parallel because it touches different files and has no
  dependency on another task.
- **[Req]**: Requirement or user story trace, such as `FR-001` or `US1`.
- Include exact file paths in each task.

## Phase 1: Workflow Setup

- [x] T001 [FR-OWN] Confirm the sibling clone exists at
      `/workspaces/homelab-ideas/sdd-skill-doc-cleanup` on
      `codex/sdd-skill-doc-cleanup`.
- [x] T002 [FR-OWN] Confirm `.codex/tmp/active-implementation`,
      `.codex/tmp/implementation-plan.yaml`,
      `.codex/tmp/implementation-owner-attestation.yaml`, and matching
      `.codex/tmp/delegation-tokens/implementation-agent-sdd-skill-doc-cleanup.token`.
- [x] T003 [FR-OWN] Run the three owner workflow validators and record outcomes
      in `specs/sdd-skill-doc-cleanup/evidence.md`.

## Phase 2: Spec And Plan

- [x] T004 [FR-SPEC] Write `specs/sdd-skill-doc-cleanup/spec.md`.
- [x] T005 [FR-PLAN] Write `specs/sdd-skill-doc-cleanup/plan.md`, including
      tiered TDD and development validation expectations.
- [x] T006 [FR-DOCS] Confirm documentation impact and generated architecture
      expectations in `specs/sdd-skill-doc-cleanup/plan.md`.

## Phase 3: Audit And Implementation

- [x] T007 [P] [FR-001] Audit tracked `.agents/skills/` and confirm only
      generated Spec Kit skills are tracked.
- [x] T008 [P] [FR-003] Audit `.codex/agents/*.toml` for stale `instructions`
      keys and update to `developer_instructions` where present.
- [x] T009 [P] [FR-004] Audit `.codex/memory/approved/*.md` and update or
      archive stale approved memory entries.
- [x] T010 [P] [FR-005] Audit `AGENTS.md`, `PLANS.md`,
      `docs/runbooks/spec-driven-development.md`,
      `docs/runbooks/implementation-workflow.md`, and `.codex/retrieval.yaml`
      for dead default-context references.
- [x] T011 [FR-IMPL] Apply the smallest targeted cleanup in the audited files.
- [x] T012 [FR-IMPL] Re-check constitution gates after implementation edits in
      `specs/sdd-skill-doc-cleanup/plan.md`.

## Phase 4: Verification

- [x] T013 [FR-TEST] Run
      `python3 tools/codex-harness/validate_sdd_context.py --marker .codex/tmp/active-implementation --root "$(pwd)" --branch "$(git branch --show-current)" --require-plan-artifacts`.
- [x] T014 [FR-TEST] Run `python3 -m unittest discover -s tools/codex-harness/tests`.
- [x] T015 [FR-TEST] Run `pre-commit run --all-files`.
- [x] T016 [FR-TEST] Run `python3 tools/architecture/render.py --check`.
- [x] T017 [FR-TEST] Run `python3 -m unittest discover -s tools/development/tests`.
- [x] T018 [FR-TEST] Run `python3 -m unittest discover -s tools/context-pack/tests`.
- [x] T019 [FR-TEST] Run
      `uv run --project tools/agent-memory pytest tools/agent-memory/tests`.
- [x] T020 [FR-TEST] Run `npx -y agnix@0.25.0 .`.
- [x] T021 [FR-TEST] Run optional `npm ci && npm test` in `tests/smoke` if
      quick, or record why skipped.
- [x] T022 [FR-SMOKE] Record development smoke profile `none` because this is
      docs-only/local agent configuration cleanup.
- [x] T023 [FR-EVIDENCE] Record command outcomes, smoke exception, final `HEAD`,
      and documentation impact in `specs/sdd-skill-doc-cleanup/evidence.md`.

## Phase 5: Commit And Handoff

- [x] T024 [FR-PR] Write `.codex/tmp/pr-summary.md` from the plan and final
      evidence.
- [x] T025 [FR-PR] Commit with a conventional commit message.
- [x] T026 [FR-PR] Report exact `HEAD` and do not create verifier approval or
      PR.

## Dependencies

- Phase 1 must pass before tracked edits beyond initial SDD bootstrap.
- Phase 2 must be non-empty before non-bootstrap implementation edits.
- Phase 3 audit tasks can run in parallel; T011 depends on their findings.
- Phase 4 depends on implementation edits.
- Phase 5 depends on evidence updates.

## Implementation Strategy

Complete the docs-only cleanup as a single increment: bootstrap SDD context,
audit the scoped files, apply targeted edits, run local checks, record evidence,
commit, and stop before verifier approval or PR creation.
