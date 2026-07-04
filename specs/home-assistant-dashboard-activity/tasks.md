# Tasks: home-assistant-dashboard-activity

**Input**: `specs/home-assistant-dashboard-activity/spec.md` and
`specs/home-assistant-dashboard-activity/plan.md`
**Risk Tier**: medium
**Prerequisites**: Valid workflow marker, implementation plan, owner
attestation, and delegation token under `.codex/tmp/`

## Format: `[ID] [P?] [Req] Description`

- **[P]**: Can run in parallel because it touches different files and has no
  dependency on another task.
- **[Req]**: Requirement or user story trace, such as `FR-001` or `US1`.
- Include exact file paths in each task.

## Phase 1: Workflow Setup

- [x] T001 [FR-OWN] Create or refresh the sibling clone at
      `/workspaces/homelab-ideas/home-assistant-dashboard-activity` on
      `codex/home-assistant-dashboard-activity`.
- [x] T002 [FR-OWN] Correct the implementation clone remote and branch base to
      current `origin/main` at `c3c4210e349f90b1027b9a21944119303329fe02`
      before tracked edits.
- [x] T003 [FR-OWN] Create `.codex/tmp/active-implementation`,
      `.codex/tmp/implementation-plan.yaml`,
      `.codex/tmp/implementation-owner-attestation.yaml`, and
      `.codex/tmp/delegation-tokens/implementation-agent-home-assistant-dashboard-activity.token`.
- [x] T004 [FR-OWN] Run the three owner workflow validators before tracked
      edits.

## Phase 2: Spec And Plan

- [x] T005 [FR-SPEC] Write
      `specs/home-assistant-dashboard-activity/spec.md`.
- [x] T006 [FR-PLAN] Write
      `specs/home-assistant-dashboard-activity/plan.md`, including tiered TDD
      and development validation expectations.
- [x] T007 [FR-DOCS] Confirm documentation impact and generated architecture
      expectations in `specs/home-assistant-dashboard-activity/plan.md`.
- [x] T008 [FR-EVIDENCE] Create initial
      `specs/home-assistant-dashboard-activity/evidence.md`.

## Phase 3: Implementation

- [x] T009 [P] [FR-001] Add the native Prometheus exporter configuration to
      `kubernetes/apps/home-assistant/config/configuration.yaml`.
- [x] T010 [P] [FR-001] Add the native Prometheus exporter configuration to
      `kubernetes/apps/home-assistant/branch/config/configuration.yaml`.
- [x] T011 [P] [FR-002] Add Prometheus scrape annotations to
      `kubernetes/apps/home-assistant/service.yaml`.
- [x] T012 [P] [FR-002] Add Prometheus scrape annotations to the branch Service
      in `kubernetes/apps/home-assistant/branch/home-assistant.yaml`.
- [x] T013 [FR-003] [FR-004] [FR-005] [FR-006] Update
      `kubernetes/infra/monitoring/grafana/dashboards/home-assistant-dashboard.json`
      with the Activity row and required panel removals.
- [x] T014 [FR-PLAN] Re-check constitution gates after implementation edits in
      `specs/home-assistant-dashboard-activity/plan.md`.

## Phase 4: Verification

- [x] T015 [FR-007] Run
      `python3 tools/codex-harness/validate_sdd_context.py --marker .codex/tmp/active-implementation --root "$(pwd)" --branch "$(git branch --show-current)" --require-plan-artifacts`.
- [x] T016 [FR-007] Run
      `jq empty kubernetes/infra/monitoring/grafana/dashboards/home-assistant-dashboard.json`.
- [x] T017 [FR-007] Run
      `kubectl kustomize kubernetes/apps/home-assistant`.
- [x] T018 [FR-007] Run
      `kubectl kustomize kubernetes/apps/home-assistant/branch`.
- [x] T019 [FR-007] Run
      `kubectl kustomize kubernetes/infra/monitoring/grafana/dashboards`.
- [x] T020 [FR-007] Run `python3 tools/architecture/render.py --check` and
      update generated architecture only if stale.
- [x] T021 [FR-007] Attempt
      `python3 tools/development/verify_branch_deploy.py --app home-assistant --branch codex/home-assistant-dashboard-activity --slug home-assistant-dashboard-activity --push`
      or record exact exception.
- [x] T022 [FR-007] Attempt Grafana/Mimir query smoke for new
      `homeassistant_*` metrics or record exact exception.
- [x] T023 [FR-007] Record command outcomes, exceptions, final `HEAD`, and
      documentation impact in `specs/home-assistant-dashboard-activity/evidence.md`.

## Phase 5: Commit And Handoff

- [x] T024 [FR-007] Write `.codex/tmp/pr-summary.md` from the plan and final
      evidence.
- [x] T025 [FR-007] Commit with a conventional commit message.
- [x] T026 [FR-007] Run the SDD context validator with `--require-evidence
      --head` after commit.
- [x] T027 [FR-007] Report exact `HEAD` and do not create verifier approval.

## Phase 6: Dashboard Activity Follow-Up

- [x] T028 [FR-004] Replace guessed Home Assistant Activity PromQL in
      `kubernetes/infra/monitoring/grafana/dashboards/home-assistant-dashboard.json`
      with exporter-semantics-based queries using
      `homeassistant_state_change_total`,
      `homeassistant_last_updated_time_seconds`,
      `homeassistant_entity_available`, `homeassistant_entity_info`,
      `homeassistant_light_brightness_percent`,
      `homeassistant_switch_state`, and
      `homeassistant_binary_sensor_state`.
- [x] T029 [FR-004] Replace zero-prone active entity stat panels in
      `kubernetes/infra/monitoring/grafana/dashboards/home-assistant-dashboard.json`
      with table panels that show rows only when matching active entity metrics
      exist.
- [x] T030 [FR-007] Record the no-development-smoke rationale for this
      dashboard-only follow-up in
      `specs/home-assistant-dashboard-activity/evidence.md`.
- [x] T031 [FR-007] Run follow-up local checks:
      `jq empty kubernetes/infra/monitoring/grafana/dashboards/home-assistant-dashboard.json`,
      `kubectl kustomize kubernetes/infra/monitoring/grafana/dashboards`, and
      `python3 tools/architecture/render.py --check`.
- [x] T032 [FR-007] Commit the focused follow-up with a conventional commit
      message.
- [x] T033 [FR-007] Run the SDD context validator with `--require-evidence
      --head` after the follow-up commit and report exact `HEAD` without
      creating verifier approval.

## Phase 7: Post-Merge Branch Rebuild

- [x] T034 [FR-007] Rebuild local branch
      `codex/home-assistant-dashboard-activity` from current `origin/main`
      after PR #336 merged the original implementation.
- [x] T035 [FR-007] Reapply only the dashboard activity follow-up delta to
      avoid duplicating original exporter/config/Service changes already merged
      through PR #336.
- [x] T036 [FR-007] Run post-rebuild local checks:
      `jq empty kubernetes/infra/monitoring/grafana/dashboards/home-assistant-dashboard.json`,
      `kubectl kustomize kubernetes/infra/monitoring/grafana/dashboards`, and
      `python3 tools/architecture/render.py --check`.
- [x] T037 [FR-007] Run the SDD context validator with `--require-evidence
      --head` after the rebuilt follow-up commit and report exact `HEAD`
      without pushing or creating verifier approval.

## Dependencies

- Phase 1 must complete before tracked edits.
- Phase 2 bootstraps durable SDD context before implementation edits.
- T009 through T012 can run in parallel because they touch separate manifest
  files.
- T013 should run after SDD bootstrap and before dashboard validation.
- Verification tasks run after implementation edits.
- Final evidence and PR summary are updated after validation and commit.
- Phase 6 is a focused follow-up after user feedback and touches only the
  dashboard JSON plus SDD/pr-summary evidence.
- Phase 7 rebuilds the branch after PR #336 merged so the follow-up PR contains
  only the dashboard activity delta relative to current `origin/main`.

## Parallel Execution Examples

- T009, T010, T011, and T012 are independent YAML edits and can be reviewed in
  parallel.
- T016 through T020 are independent local checks once implementation files are
  stable.

## Implementation Strategy

Deliver exporter configuration and Service scraping first so the metrics source
is present, then update the dashboard to consume native Home Assistant metrics.
Keep validation focused on local renders and schema checks, with best-effort
development branch and live metric smoke attempts recorded for verifier review.
