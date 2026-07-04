# Evidence: immich-dashboard-stats

**Branch**: `codex/immich-dashboard-stats`
**Risk Tier**: medium
**Started**: 2026-07-04

## Spec Kit Initialization

- Command: manual artifact creation from repo templates after user-approved
  implementation plan.
- Outcome: PASS
- Spec Kit version: not reinitialized; existing repo Spec Kit structure used.
- Integration: existing repository integration.
- Fallback: `/workspaces/homelab-worktrees` was not writable, so the
  implementation worktree is `/workspaces/homelab-ideas/immich-dashboard-stats`.

## Workflow Validation

| Command | Result | Notes |
| ------- | ------ | ----- |
| `git worktree add /workspaces/homelab-worktrees/immich-dashboard-stats -b codex/immich-dashboard-stats origin/main` | FAIL | Parent directory could not be created: permission denied. |
| `git worktree add /workspaces/homelab-ideas/immich-dashboard-stats -b codex/immich-dashboard-stats origin/main` | PASS | Worktree created from `origin/main`. |
| `python3 tools/codex-harness/validate_sdd_context.py --root "$(pwd)" --branch "$(git branch --show-current)" --require-plan-artifacts` | PASS | SDD context validated after spec, plan, tasks, and evidence existed. |

## Query Smoke

Strict pass rule: every dashboard query must return at least one series, stream,
log line, or an intentional zero-valued fallback vector.

| Query | Result | Notes |
| ----- | ------ | ----- |
| PromQL dashboard matrix | PASS | `scrape_health=1`, `users=1`, `new_assets=1.3167/sec`, API CPU and memory returned live series. Queue, job, and processing panels returned intentional zero fallback before the new `8082` scrape Service exists in Mimir. |
| Raw `8082` metric family smoke | PASS | Live `immich-server:8082/metrics` exposes queue, job, media, ML, and storage metric families needed by the dashboard. |
| Loki warning/error query | PASS | Returned Immich upload/thumbnail/face/error log streams from Loki. |
| Full dashboard PromQL parse smoke via Mimir port-forward | PASS | Checked 37 Prometheus targets from `immich-dashboard.json`; all returned success and at least one series, including intentional zero fallback vectors where the new `8082` scrape target is not reconciled yet. |

## Local Checks

| Command | Result | Notes |
| ------- | ------ | ----- |
| `jq empty kubernetes/infra/monitoring/grafana/dashboards/immich-dashboard.json` | PASS | Dashboard JSON parsed successfully. |
| `git diff --check` | PASS | No whitespace errors. |
| `kubectl kustomize kubernetes/apps/immich` | PASS | Rendered the app and included `Service/immich-server-metrics-ms`; output stored at `/tmp/immich-app-render.yaml`. |
| `export branch_slug=immich-dashboard-stats cluster_domain=dev.lab.petebeegle.com; kubectl kustomize kubernetes/apps/immich/branch \| flux envsubst --strict` | PASS | Rendered branch overlay with `Service/immich-server-metrics-ms` in namespace `immich-immich-dashboard-stats`; output stored at `/tmp/immich-branch-render.yaml`. |
| `kubectl kustomize kubernetes/infra/monitoring/grafana/dashboards` | PASS | Rendered dashboard ConfigMaps and `GrafanaDashboard` resources; output stored at `/tmp/grafana-dashboards-render.yaml`. |
| `kubectl kustomize kubernetes/infra/monitoring/grafana` | PASS | Rendered parent Grafana kustomization; output stored at `/tmp/grafana-render.yaml`. |
| `python3 tools/architecture/render.py --check` | PASS | Failed before generated docs refresh, passed after `python3 tools/architecture/render.py --write`. |

## Automated Smoke And Live Verification

| Target | Method | Result | Notes |
| ------ | ------ | ------ | ----- |
| `up{namespace="immich",service="immich-server-metrics-ms"}` | Post-merge production Mimir query | PENDING | New scrape target is not expected to exist until Flux applies the PR. |

## Deployment State

- Source fetched SHA: not merged/reconciled during implementation.
- Target applied SHA: not merged/reconciled during implementation.
- Live resource spec checked: local render verifies intended `Service/immich-server-metrics-ms`; live Mimir verification remains post-merge.
- Gateway/listener/DNS/certificate checked: N/A, no route changes.
- Exact user-facing URL result: N/A, dashboard-only observability change.

## Development Validation

- Profile: none
- Branch slug: immich-dashboard-stats
- HEAD: branch working tree based on `35b1785` before local commit.
- Report path: N/A
- Cleanup: N/A
- Result or exception: PASS by documented substitute. Development validation is substituted by production
  read-only query smoke and local render checks because development does not
  carry equivalent production Immich upload/processing observability history.

## Documentation Impact

- Updated: `specs/immich-dashboard-stats/`, `docs/architecture.md`.
- Generated docs: `docs/architecture.md` refreshed to include `metrics-service.yaml`.
- No-docs rationale: existing Immich runbook still accurately describes dashboard ownership; this change adds panels and scrape coverage only.

## SDD Conformance

- Local sources checked: `docs/runbooks/spec-driven-development.md`,
  `docs/runbooks/implementation-workflow.md`.
- Upstream Spec Kit sources checked: N/A; no workflow/template behavior change.
- Spec -> Plan -> Tasks -> Implement alignment: PASS. The implementation follows the requested dashboard and scrape-target plan.
- Artifact updates after implementation: PASS. Tasks and evidence were updated after implementation and validation.

## Exceptions And Follow-Ups

- Worktree path exception: `/workspaces/homelab-worktrees` is not writable.
- Follow-up after merge/reconcile: confirm
  `up{namespace="immich",service="immich-server-metrics-ms"}` appears in Mimir.

## Final State

- Final branch: `codex/immich-dashboard-stats`
- Final HEAD: local implementation commit; verify with `git log -1`.
- Commit: `feat(immich): add user-oriented dashboard stats`
