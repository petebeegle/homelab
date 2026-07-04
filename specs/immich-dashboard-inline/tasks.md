# Tasks: immich-dashboard-inline

**Input**: `specs/immich-dashboard-inline/spec.md` and
`specs/immich-dashboard-inline/plan.md`
**Risk Tier**: medium

## Phase 1: Spec And Plan

- [X] T001 [FR-SPEC] Create `specs/immich-dashboard-inline/spec.md`.
- [X] T002 [FR-PLAN] Create `specs/immich-dashboard-inline/plan.md`.
- [X] T003 [FR-DOCS] Identify generated architecture impact.

## Phase 2: Implementation

- [X] T004 [FR-001] Convert `kubernetes/infra/monitoring/grafana/dashboards/immich-dashboard.yaml` to inline `spec.json`.
- [X] T005 [FR-002] Remove the Immich dashboard ConfigMap generator from `kubernetes/infra/monitoring/grafana/dashboards/kustomization.yaml`.
- [X] T006 [FR-002] Remove `kubernetes/infra/monitoring/grafana/dashboards/immich-dashboard.json`.
- [X] T007 [FR-DOCS] Update generated architecture if required.

## Phase 3: Verification

- [X] T008 [FR-TEST] Render Grafana dashboards and parent kustomization.
- [X] T009 [FR-TEST] Parse rendered inline Immich dashboard JSON with `jq`.
- [X] T010 [FR-TEST] Run generated architecture check.
- [X] T011 [FR-TEST] Run SDD context validation.
- [X] T012 [FR-EVIDENCE] Record command outcomes and post-merge verification expectation.

## Phase 4: Commit And PR

- [X] T013 [FR-PR] Commit with a conventional commit message.
- [ ] T014 [FR-PR] Push branch and open a draft PR.
