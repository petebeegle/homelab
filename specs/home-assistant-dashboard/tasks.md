# Tasks: home-assistant-dashboard

**Input**: `specs/home-assistant-dashboard/spec.md` and
`specs/home-assistant-dashboard/plan.md`
**Risk Tier**: medium
**Prerequisites**: Valid workflow marker, implementation plan, owner attestation,
and delegation token under `.codex/tmp/`

## Phase 1: Workflow Setup

- [x] T001 [FR-OWN] Create the sibling clone at `/workspaces/homelab-ideas/home-assistant-dashboard` on `codex/home-assistant-dashboard`.
- [x] T002 [FR-OWN] Create `.codex/tmp/active-implementation`, `.codex/tmp/implementation-plan.yaml`, `.codex/tmp/implementation-owner-attestation.yaml`, and matching delegation token evidence.
- [x] T003 [FR-OWN] Run the three owner workflow validators.

## Phase 2: Spec And Plan

- [x] T004 [FR-SPEC] Write `specs/home-assistant-dashboard/spec.md`.
- [x] T005 [FR-PLAN] Write `specs/home-assistant-dashboard/plan.md`.
- [x] T006 [FR-DOCS] Confirm documentation impact and generated architecture expectations.

## Phase 3: Implementation

- [x] T007 [FR-004] Run strict non-empty production query smoke before tracked dashboard edits.
- [x] T008 [P] [FR-001] Add Home Assistant folder to `kubernetes/infra/monitoring/grafana/folders.yaml`.
- [x] T009 [P] [FR-002] Add `kubernetes/infra/monitoring/grafana/dashboards/home-assistant-dashboard.yaml`.
- [x] T010 [P] [FR-002] Add `kubernetes/infra/monitoring/grafana/dashboards/home-assistant-dashboard.json`.
- [x] T011 [FR-002] Register the dashboard in `kubernetes/infra/monitoring/grafana/dashboards/kustomization.yaml`.
- [x] T012 [FR-IMPL] Re-check constitution gates after implementation edits.

## Phase 4: Verification

- [x] T013 [FR-TEST] Run `jq empty kubernetes/infra/monitoring/grafana/dashboards/home-assistant-dashboard.json`.
- [x] T014 [FR-TEST] Run `kubectl kustomize kubernetes/infra/monitoring/grafana/dashboards`.
- [x] T015 [FR-TEST] Run `python3 tools/architecture/render.py --check`.
- [x] T016 [FR-TEST] Run `python3 tools/codex-harness/validate_sdd_context.py --marker .codex/tmp/active-implementation --root "$(pwd)" --branch "$(git branch --show-current)" --require-plan-artifacts`.
- [x] T017 [FR-EVIDENCE] Record command outcomes, smoke evidence, exceptions, and final `HEAD` in `specs/home-assistant-dashboard/evidence.md`.

## Phase 5: Commit And Handoff

- [x] T018 [FR-PR] Write `.codex/tmp/pr-summary.md` from the plan and final evidence.
- [x] T019 [FR-PR] Commit with a conventional commit message.
- [x] T020 [FR-PR] Report exact `HEAD` and do not create verifier approval.
