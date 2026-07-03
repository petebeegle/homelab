---
description: "Homelab SDD task list for Home Assistant Hue V2 onboarding boundary"
---

# Tasks: home-assistant-hue-v2

**Input**: `specs/home-assistant-hue-v2/spec.md` and
`specs/home-assistant-hue-v2/plan.md`
**Risk Tier**: tiny
**Prerequisites**: Valid workflow marker, implementation plan, owner attestation,
and delegation token under `.codex/tmp/`

## Format: `[ID] [P?] [Req] Description`

- **[P]**: Can run in parallel because it touches different files and has no dependency on another task.
- **[Req]**: Requirement or user story trace, such as `FR-001` or `US1`.
- Include exact file paths in each task.

## Phase 1: Workflow Setup

- [x] T001 [FR-OWN] Create the sibling clone at `/workspaces/homelab-ideas/home-assistant-hue-v2` on `codex/home-assistant-hue-v2`.
- [x] T002 [FR-OWN] Create `.codex/tmp/active-implementation`, `.codex/tmp/implementation-plan.yaml`, `.codex/tmp/implementation-owner-attestation.yaml`, and matching delegation token evidence.
- [x] T003 [FR-OWN] Run the three owner workflow validators and record outcomes in `specs/home-assistant-hue-v2/evidence.md`.

## Phase 2: Spec And Plan

- [x] T004 [FR-SPEC] Write `specs/home-assistant-hue-v2/spec.md`.
- [x] T005 [FR-PLAN] Write `specs/home-assistant-hue-v2/plan.md`, including docs-only/tiny validation expectations.
- [x] T006 [FR-DOCS] Confirm documentation impact and generated architecture expectations.

## Phase 3: Implementation

- [x] T007 [P] [FR-001] Edit `docs/runbooks/home-assistant.md` to document Hue V2 UI pairing as runtime config-flow state on the PVC.
- [x] T008 [P] [FR-002] Edit `docs/runbooks/home-assistant.md` to exclude Hue `.storage`, config entries, credentials, tokens, and fake integration config from Git.
- [x] T009 [P] [FR-003] Edit `docs/runbooks/home-assistant.md` to list required post-pairing inventory before Git-owned Hue packages or automations.
- [x] T010 [FR-004] Confirm no placeholder `hue.yaml` package is added.
- [x] T011 [FR-IMPL] Re-check constitution gates after implementation edits.

## Phase 4: Verification

- [x] T012 [FR-TEST] Run `python3 tools/codex-harness/validate_sdd_context.py --marker .codex/tmp/active-implementation --root "$(pwd)" --branch "$(git branch --show-current)" --require-plan-artifacts`.
- [x] T013 [FR-TEST] Run `git diff --check`.
- [x] T014 [FR-TEST] Review `git diff --name-only` and `git status --short`.
- [x] T015 [FR-TEST] Run targeted diff/grep checks proving no Hue runtime files, config entries, tokens, credentials, or placeholder package were added.
- [x] T016 [FR-SMOKE] Record development smoke profile `none` because this is docs-only and Hue pairing requires physical bridge/UI runtime access.
- [x] T017 [FR-EVIDENCE] Record command outcomes, smoke exception, and branch handoff state in `specs/home-assistant-hue-v2/evidence.md`.

## Phase 5: Commit And Handoff

- [x] T018 [FR-PR] Write `.codex/tmp/pr-summary.md` from the plan and final evidence.
- [x] T019 [FR-PR] Commit with a conventional commit message.
- [x] T020 [FR-PR] Report exact commit SHA and do not create verifier approval.
