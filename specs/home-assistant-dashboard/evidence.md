# Evidence: home-assistant-dashboard

**Branch**: `codex/home-assistant-dashboard`
**Risk Tier**: medium
**Started**: 2026-07-03
**Owner**: implementation-agent-home-assistant-dashboard

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

Strict pass rule: every included dashboard query must return at least one series, stream, or log line.

| Query | Result | Notes |
| ----- | ------ | ----- |
| `kube_pod_status_phase{exported_namespace="home-assistant",pod=~"home-assistant-.*"}` | PASS | 5 series. |
| `kube_deployment_status_replicas_ready{exported_namespace="home-assistant",deployment="home-assistant"}` | PASS | 1 series. |
| `increase(kube_pod_container_status_restarts_total{exported_namespace="home-assistant",container="home-assistant"}[24h])` | PASS | 3 series. |
| `kube_persistentvolumeclaim_status_phase{exported_namespace="home-assistant",persistentvolumeclaim="home-assistant-config"}` | PASS | 3 series. |
| `gatewayapi_httproute_parent_accepted{exported_namespace="home-assistant",name="home-assistant"}` | PASS | 2 series. |
| `gatewayapi_httproute_parent_resolved_refs{exported_namespace="home-assistant",name="home-assistant"}` | PASS | 2 series. |
| `rate(container_cpu_usage_seconds_total{namespace="home-assistant",pod=~"home-assistant-.*",container="home-assistant"}[5m])` | PASS | 2 series. |
| `container_memory_working_set_bytes{namespace="home-assistant",pod=~"home-assistant-.*",container="home-assistant"}` | PASS | 2 series. |
| `sum(count_over_time({namespace="synthetics", app="synthetic-smoke"} \|= "SMOKE_RUN_SUMMARY" \| logfmt \| status="failed" [30m])) OR vector(0)` | PASS | 1 series, sample value 0. |
| `kube_pod_status_phase{exported_namespace="synthetics",pod=~"synthetic-smoke-.*"}` | PASS | 75 series. |
| `{namespace="home-assistant", container="home-assistant"}` | PASS | 5 streams, 20 sampled lines. |
| `{namespace="home-assistant", container="home-assistant"} \|~ "(?i)(warning\|error\|exception\|failed\|timeout\|traceback\|invalid\|auth\|oidc\|onboarding)"` | PASS | 3 streams, 6 sampled lines. |
| `{namespace="home-assistant", container="home-assistant"} \|~ "(?i)(integration\|setup\|custom_components\|config_entry\|platform\|device\|entity)" !~ "(?i)(homeassistant\\.config].*package\|invalid package definition\|packages/)"` | PASS | Narrowed from the previously smoke-tested integration activity query to exclude Home Assistant package/config-definition errors such as invalid `packages/code-first.yaml` slug noise. |
| `{namespace="synthetics", app="synthetic-smoke"} \|= "SMOKE_RUN_SUMMARY"` | PASS | 20 streams, 20 sampled lines. |
| `{namespace="synthetics", app="synthetic-smoke"} \|~ "(?i)(home assistant\|homeassistant\|authentik\|oidc\|onboarding)"` | PASS | 9 streams, 20 sampled lines. |

## Local Checks

| Command | Result | Notes |
| ------- | ------ | ----- |
| `jq empty kubernetes/infra/monitoring/grafana/dashboards/home-assistant-dashboard.json` | PASS | Dashboard JSON parsed successfully. |
| `kubectl kustomize kubernetes/infra/monitoring/grafana/dashboards` | PASS | Rendered dashboard ConfigMap and `GrafanaDashboard`; output stored at `.codex/tmp/grafana-dashboards.render.yaml`. |
| `kubectl kustomize kubernetes/infra/monitoring/grafana` | PASS | Rendered parent Grafana kustomization with the Home Assistant folder; output stored at `.codex/tmp/grafana.render.yaml`. |
| `python3 tools/architecture/render.py --check` | PASS | Failed before generated docs refresh, passed after `python3 tools/architecture/render.py --write`. |
| `python3 tools/codex-harness/validate_sdd_context.py ... --require-plan-artifacts` | PASS | SDD context validated after spec, plan, tasks, and evidence existed. |

## Follow-Up Filter Evidence

| Command | Result | Notes |
| ------- | ------ | ----- |
| Python regex check against reported `packages/code-first.yaml` log line | PASS | Include regex matched, exclusion regex matched, final display decision was `False`. |
| `source scripts/kube-aliases.sh && kd config current-context` | PASS | Confirmed `admin@homelab-development`. |
| `source scripts/kube-aliases.sh && kd get crd grafanadashboards.grafana.integreatly.org grafanafolders.grafana.integreatly.org` | PASS | Development cluster has the required Grafana Operator CRDs. |
| `source scripts/kube-aliases.sh && kd apply --server-side --dry-run=server -f kubernetes/infra/monitoring/grafana/dashboards/home-assistant-dashboard.yaml` | BLOCKED | Development API server rejected the namespaced resource because namespace `grafana` does not exist in development. |
| `source scripts/kube-aliases.sh && kp -n home-assistant logs <pod> --since=24h` with the dashboard include/exclude regexes | PASS | Production pod logs had 1 integration-activity match before the exclusion and 1 after it; the narrowed signal is non-empty. |

## Development Validation

- Profile: none
- Branch slug: N/A
- HEAD: pending
- Report path: N/A
- Cleanup: N/A
- Result or exception: Development cluster validation is not used because the development cluster lacks the production Home Assistant observability history required by the strict non-empty dashboard query gate. Substitute checks are production read-only query smoke plus local JSON/render validation.

## Documentation Impact

- Updated: `specs/home-assistant-dashboard/`
- Generated docs: `docs/architecture.md`
- No-docs rationale: Dashboard behavior is captured in SDD artifacts; no operator runbook behavior changes.

## Exceptions And Follow-Ups

- Runtime Home Assistant integration inventory remains future work through a dedicated exporter or authenticated API path.
- Self-implementation fallback used because subagent spawning is restricted unless subagents are explicitly requested; the user explicitly requested implementation.

## Final State

- Final branch: `codex/home-assistant-dashboard`
- Final HEAD: Recorded after commit in `.codex/tmp/pr-summary.md` and final handoff.
- Commit: `feat(grafana): add home assistant dashboard`; exact final SHA is recorded in runtime handoff context after commit.
- Verifier approval: not created by implementation owner
