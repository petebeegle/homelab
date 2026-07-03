# Evidence: arr-stack-dashboard

**Branch**: `codex/arr-stack-dashboard`
**Risk Tier**: medium
**Started**: 2026-07-03
**Owner**: implementation-agent-arr-stack-dashboard

## Spec Kit Initialization

- Command: N/A; existing Spec Kit templates were used.
- Outcome: Existing repository SDD scaffolding reused.
- Spec Kit version: N/A
- Integration: existing repository integration
- Fallback: N/A

## Workflow Validation

| Command | Result | Notes |
| ------- | ------ | ----- |
| `python3 tools/codex-harness/validate_active_implementation.py ...` | PASS | Validated before tracked edits. |
| `python3 tools/codex-harness/validate_implementation_plan.py ...` | PASS | Validated before tracked edits. |
| `python3 tools/codex-harness/validate_workflow_attestations.py --kind owner ...` | PASS | Validated before tracked edits. |

## Query Smoke

Strict pass rule: every included dashboard query family must return at least one series, stream, or log line.

Namespace regex: `prowlarr|qbittorrent|radarr|sabnzbd|sonarr|whisparr`

| Query Family | Result | Notes |
| ------------ | ------ | ----- |
| `kube_pod_status_phase{exported_namespace=~"prowlarr\|qbittorrent\|radarr\|sabnzbd\|sonarr\|whisparr"}` | PASS | 30 series. |
| `kube_deployment_status_replicas_ready{exported_namespace=~"prowlarr\|qbittorrent\|radarr\|sabnzbd\|sonarr\|whisparr"}` | PASS | 6 series. |
| `increase(kube_pod_container_status_restarts_total{exported_namespace=~"prowlarr\|qbittorrent\|radarr\|sabnzbd\|sonarr\|whisparr",container!="POD",container!=""}[24h])` | PASS | 20 series. |
| `rate(container_cpu_usage_seconds_total{namespace=~"prowlarr\|qbittorrent\|radarr\|sabnzbd\|sonarr\|whisparr",container!="POD",container!=""}[5m])` | PASS | 22 series. |
| `container_memory_working_set_bytes{namespace=~"prowlarr\|qbittorrent\|radarr\|sabnzbd\|sonarr\|whisparr",container!="POD",container!=""}` | PASS | 22 series. |
| `kube_persistentvolumeclaim_status_phase{exported_namespace=~"prowlarr\|qbittorrent\|radarr\|sabnzbd\|sonarr\|whisparr"}` | PASS | 24 series. |
| `gatewayapi_httproute_parent_accepted{exported_namespace=~"prowlarr\|qbittorrent\|radarr\|sabnzbd\|sonarr\|whisparr"}` | PASS | 12 series. |
| `gatewayapi_httproute_parent_resolved_refs{exported_namespace=~"prowlarr\|qbittorrent\|radarr\|sabnzbd\|sonarr\|whisparr"}` | PASS | 12 series. |
| `{namespace=~"prowlarr\|qbittorrent\|radarr\|sabnzbd\|sonarr\|whisparr"}` | PASS | 2 streams, 20 sampled lines. |
| `{namespace=~"prowlarr\|qbittorrent\|radarr\|sabnzbd\|sonarr\|whisparr"} \|~ "(?i)(warning\|warn\|error\|exception\|failed\|timeout\|traceback\|invalid\|denied\|unhealthy)"` | PASS | 2 streams, 20 sampled lines. |
| `{namespace=~"prowlarr\|qbittorrent\|radarr\|sabnzbd\|sonarr\|whisparr"} \|~ "(?i)(download\|import\|grab\|queue\|indexer\|torrent\|sabnzbd\|qbittorrent\|radarr\|sonarr\|prowlarr\|whisparr)"` | PASS | 4 streams, 20 sampled lines. |

## Local Checks

| Command | Result | Notes |
| ------- | ------ | ----- |
| `jq empty kubernetes/infra/monitoring/grafana/dashboards/arr-stack-dashboard.json` | PASS | Dashboard JSON parsed successfully. |
| `kubectl kustomize kubernetes/infra/monitoring/grafana/dashboards` | PASS | Rendered dashboard ConfigMap and `GrafanaDashboard`; output stored at `.codex/tmp/grafana-dashboards.render.yaml`. |
| `kubectl kustomize kubernetes/infra/monitoring/grafana` | PASS | Rendered parent Grafana kustomization with the Arr Stack folder; output stored at `.codex/tmp/grafana.render.yaml`. |
| `python3 tools/architecture/render.py --check` | PASS | Failed before generated docs refresh, passed after `python3 tools/architecture/render.py --write`. |
| `python3 tools/codex-harness/validate_sdd_context.py ... --require-plan-artifacts` | PASS | SDD context validated after spec, plan, tasks, and evidence existed. |

## Development Validation

- Profile: none
- Branch slug: N/A
- HEAD: pending
- Report path: N/A
- Cleanup: N/A
- Result or exception: Development cluster validation is not used because the development cluster lacks the private arr stack observability history required by the strict non-empty dashboard query gate. Substitute checks are production read-only query smoke plus local JSON/render validation.

## Documentation Impact

- Updated: `specs/arr-stack-dashboard/`
- Generated docs: `docs/architecture.md`
- No-docs rationale: Dashboard behavior is captured in SDD artifacts; no operator runbook behavior changes.

## Exceptions And Follow-Ups

- App API-level queue/library health remains future work through per-app exporters or authenticated API data sources.

## Final State

- Final branch: `codex/arr-stack-dashboard`
- Final HEAD: Recorded after commit in `.codex/tmp/pr-summary.md` and final handoff.
- Commit: `feat(grafana): add arr stack dashboard`; exact final SHA is recorded in runtime handoff context after commit.
- Verifier approval: not created by implementation owner
