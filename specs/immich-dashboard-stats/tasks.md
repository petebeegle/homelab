# Tasks: immich-dashboard-stats

**Input**: `specs/immich-dashboard-stats/spec.md` and
`specs/immich-dashboard-stats/plan.md`
**Risk Tier**: medium
**Prerequisites**: Branch `codex/immich-dashboard-stats` and matching
`specs/immich-dashboard-stats/` artifacts.

## Format: `[ID] [P?] [Req] Description`

- **[P]**: Can run in parallel or fan out to a helper lane because it touches
  different files or performs read-only validation and has no dependency on
  another incomplete task.
- **[Req]**: Requirement or user story trace, such as `FR-001` or `US1`.

## Phase 1: Spec And Plan

- [X] T001 [FR-SPEC] Create `specs/immich-dashboard-stats/spec.md`.
- [X] T002 [FR-PLAN] Create `specs/immich-dashboard-stats/plan.md`,
      including tiered TDD and development validation expectations.
- [X] T003 [FR-DOCS] Confirm documentation impact and generated architecture
      expectations.

## Phase 2: Query Smoke

- [X] T004 [P] [FR-003] Run production read-only PromQL smoke for intended
      Immich dashboard queries.
- [X] T005 [P] [FR-003] Run production read-only Loki smoke for intended
      Immich warning/error logs.

## Phase 3: Implementation

- [X] T006 [FR-001] Add
      `kubernetes/apps/immich/base/metrics-service.yaml` and register it in
      `kubernetes/apps/immich/base/kustomization.yaml`.
- [X] T007 [FR-003] Replace user-oriented panels in
      `kubernetes/infra/monitoring/grafana/dashboards/immich-dashboard.json`.
- [X] T008 [FR-DOCS] Update generated architecture if `render.py --check`
      requires it.

## Phase 4: Verification

- [X] T009 [FR-TEST] Run `jq empty kubernetes/infra/monitoring/grafana/dashboards/immich-dashboard.json`.
- [X] T010 [FR-TEST] Run `kubectl kustomize kubernetes/apps/immich`.
- [X] T011 [FR-TEST] Run branch overlay render with `flux envsubst --strict`.
- [X] T012 [FR-TEST] Run Grafana dashboard and parent kustomize renders.
- [X] T013 [FR-TEST] Run `python3 tools/architecture/render.py --check`.
- [X] T014 [FR-TEST] Run SDD context validation.
- [X] T015 [FR-SMOKE] Record development validation exception and post-merge
      microservices scrape verification expectation.
- [X] T016 [FR-EVIDENCE] Record command outcomes, smoke evidence, exceptions,
      and final `HEAD` in `specs/immich-dashboard-stats/evidence.md`.

## Phase 5: Commit And PR

- [X] T017 [FR-PR] Commit with a conventional commit message.
- [ ] T018 [FR-PR] Push branch `codex/immich-dashboard-stats` and open a PR if
      requested.
