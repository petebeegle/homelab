---
description: "Homelab SDD task list for pretty Discord alert triage cards"
---

# Tasks: pretty-discord-alert-triage-cards

**Input**: `specs/pretty-discord-alert-triage-cards/spec.md` and
`specs/pretty-discord-alert-triage-cards/plan.md`
**Risk Tier**: medium
**Prerequisites**: Branch `codex/pretty-discord-alert-triage-cards`, requested sibling clone, and matching `specs/pretty-discord-alert-triage-cards/` artifacts.

## Format: `[ID] [P?] [Req] Description`

- **[P]**: Can run in parallel because it touches different files and has no dependency on another task.
- **[Req]**: Requirement or user story trace, such as `FR-001` or `US1`.

## Phase 1: Spec And Plan

- [x] T001 [FR-SPEC] Create `specs/pretty-discord-alert-triage-cards/spec.md`.
- [x] T002 [FR-PLAN] Create `specs/pretty-discord-alert-triage-cards/plan.md`, including medium-tier TDD and development validation expectations.
- [x] T003 [FR-DOCS] Confirm documentation impact and generated architecture expectations in `specs/pretty-discord-alert-triage-cards/plan.md`.
- [x] T004 [FR-WORKFLOW] Create and validate `.codex/tmp/active-implementation`, `.codex/tmp/implementation-plan.yaml`, `.codex/tmp/implementation-owner-attestation.yaml`, and matching delegation token evidence.

## Phase 2: Implementation

- [x] T005 [FR-001] Update `kubernetes/infra/monitoring/pretty-discord-alerts/deployment.yaml` to image `ghcr.io/petebeegle/pretty-discord-alerts:1.4.0`.
- [x] T006 [FR-002] Update `kubernetes/infra/monitoring/pretty-discord-alerts/deployment.yaml` so `LOG_LEVEL` is `info`.
- [x] T007 [FR-006] Re-check constitution gates after implementation edits in `specs/pretty-discord-alert-triage-cards/plan.md`.

## Phase 3: Verification

- [x] T008 [FR-003,FR-004] Record upstream PR #3, tag `v1.4.0`, workflow run `28707784208`, GHCR digest, and platform evidence in `specs/pretty-discord-alert-triage-cards/evidence.md`.
- [x] T009 [FR-TEST] Run owner workflow validators and record results in `specs/pretty-discord-alert-triage-cards/evidence.md`.
- [x] T010 [FR-TEST] Run `kubectl kustomize kubernetes/infra/monitoring/pretty-discord-alerts` and record the result.
- [x] T011 [FR-TEST] Run `python3 tools/architecture/render.py --check` and record the result.
- [x] T012 [FR-SDD] Run required SDD/context validator and record the result.
- [x] T013 [FR-007] Attempt development-cluster validation or record exact blocker and substitute checks.
- [x] T014 [FR-005] Record that one operator-visible Grafana/relay test alert remains required before verifier approval or merge readiness.
- [x] T015 [FR-EVIDENCE] Record command outcomes, smoke evidence, exceptions, and final local state in `specs/pretty-discord-alert-triage-cards/evidence.md`.

## Phase 4: Commit And PR

- [x] T016 [FR-PR] Commit with a conventional commit message.
- [x] T017 [FR-PR] Stop before verifier approval, verifier attestation, push, or PR creation.
