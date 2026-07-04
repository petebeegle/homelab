# Evidence: immich-dashboard-inline

**Branch**: `codex/immich-dashboard-inline`
**Risk Tier**: medium
**Started**: 2026-07-04

## Diagnosis

| Check | Result | Notes |
| ----- | ------ | ----- |
| Flux source and Kustomizations | PASS | `flux-system`, `app-immich`, and `grafana` applied `main@sha1:dfb630d...`. |
| `Service/immich-server-metrics-ms` | PASS | New service exists in namespace `immich`. |
| Mimir `up{service="immich-server-metrics-ms"}` | PASS | New target is scraped and queue/job metrics are live. |
| `ConfigMap/immich-dashboard` | PASS | Contains the new panel titles. |
| Grafana API `uid=immich-overview` | FAIL | Still served the old 7-panel dashboard, proving ConfigMap content updates did not force dashboard import. |

## Local Checks

| Command | Result | Notes |
| ------- | ------ | ----- |
| `kubectl kustomize kubernetes/infra/monitoring/grafana/dashboards` | PASS | Rendered `GrafanaDashboard/immich-overview` with inline `spec.json`; output stored at `/tmp/grafana-dashboards-inline-render.yaml`. |
| `kubectl kustomize kubernetes/infra/monitoring/grafana` | PASS | Parent Grafana kustomization rendered; output stored at `/tmp/grafana-inline-render.yaml`. |
| `jq empty /tmp/immich-inline-dashboard.json` | PASS | Extracted from rendered `GrafanaDashboard.spec.json`; dashboard has UID `immich-overview` and 13 panels. |
| `python3 tools/architecture/render.py --check` | PASS | No generated architecture update required. |
| `python3 tools/codex-harness/validate_sdd_context.py --root "$(pwd)" --branch "$(git branch --show-current)" --require-plan-artifacts` | PASS | SDD context validated. |

## Post-Merge Verification

| Target | Method | Result | Notes |
| ------ | ------ | ------ | ----- |
| Grafana dashboard `immich-overview` | Grafana API | PENDING | Confirm panels include `Active Background Queues`, `Job Success / Min`, and `Recent Immich Warnings And Work Logs`. |

## Exceptions And Follow-Ups

- No live mutation was made; fix is GitOps-only.

## Final State

- Final branch: `codex/immich-dashboard-inline`
- Final HEAD: local implementation commit; verify with `git log -1`.
- Commit: `fix(grafana): inline immich dashboard json`
