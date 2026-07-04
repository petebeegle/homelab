# Evidence: fix-immich-cnpg-scrape

**Branch**: `codex/fix-immich-cnpg-scrape`
**Risk Tier**: high
**Started**: 2026-07-04

## Spec Kit Initialization

- Command: manual artifact creation from `.specify/templates/*`
- Outcome: PASS
- Spec Kit version: not invoked; local templates already present
- Integration: codex repository templates
- Fallback: `/workspaces/homelab-worktrees` was not writable, so the worktree
  was created at `/workspaces/homelab-ideas/fix-immich-cnpg-scrape`.

## Alert Triage Evidence

| Command | Result | Notes |
| ------- | ------ | ----- |
| Grafana MCP alert/query APIs | FAIL | API returned `401 Unauthorized`; switched to production kubeconfig and direct Mimir query. |
| `kubectl --kubeconfig=$HOME/.kube/homelab-production.config -n alloy get ds,pods -o wide` | PASS | Alloy DaemonSet desired/current/ready all `5`; all Alloy pods ready. |
| Direct Mimir query: `up{job=~"prometheus.scrape.*|kubelet-.*"} == 0` with tenant `anonymous` | PASS | Active down targets were `immich-postgres-r`, `immich-postgres-ro`, and `immich-postgres-rw` on `:9187`. |
| Direct Mimir query: `up{namespace="immich"}` with tenant `anonymous` | PASS | `prometheus.scrape.pods` target for `immich-postgres-1` on `:9187` was up; the three generated PostgreSQL service targets were down. |
| `kubectl --kubeconfig=$HOME/.kube/homelab-production.config -n immich get svc,endpoints,endpointslices` | PASS | PostgreSQL services expose only `5432`; generated services do not expose `9187`. |

## Workflow Validation

| Command | Result | Notes |
| ------- | ------ | ----- |
| `python3 tools/codex-harness/validate_sdd_context.py --root "$(pwd)" --branch "$(git branch --show-current)" --require-plan-artifacts` | PASS | SDD artifacts present on branch `codex/fix-immich-cnpg-scrape`. |

## Local Checks

| Command | Result | Notes |
| ------- | ------ | ----- |
| `kubectl kustomize kubernetes/infra/monitoring/alloy` | PASS | Rendered Alloy ConfigMap includes `__meta_kubernetes_service_label_cnpg_io_cluster` drop rule. |
| `helm template immich oci://ghcr.io/immich-app/immich-charts/immich --version 0.13.1 --namespace immich -f kubernetes/apps/immich/base/values.yaml` | PASS | Immich server metrics service still renders `:8081`; chart templating succeeds. |
| `kubectl kustomize kubernetes/apps/immich` | PASS | CloudNativePG `inheritedMetadata` still annotates PostgreSQL resources for pod metrics on `9187`. |
| `kubectl kustomize kubernetes/clusters/production` | PASS | Production Flux entrypoint renders successfully; nested component content is validated by the Alloy render above. |
| `git diff --check` | PASS | No whitespace errors. |

## Automated Smoke And Live Verification

| Target | Method | Result | Notes |
| ------ | ------ | ------ | ----- |
| Production Mimir `up{namespace="immich"}` | direct query through read-only port-forward | PASS | Before fix, pod target was up and generated service targets were down. |

## Deployment State

- Source fetched SHA: pending PR merge
- Target applied SHA: pending PR merge
- Live resource spec checked: pre-fix production service and pod specs checked
- Gateway/listener/DNS/certificate checked: N/A
- Exact user-facing URL result: N/A

## Development Validation

- Profile: none
- Branch slug: N/A
- HEAD: pending
- Report path: N/A
- Cleanup: N/A
- Result or exception: Development validation is not representative because the
  default development cluster does not run the production monitoring stack and
  cannot exercise the Alloy/Mimir target set. Substitute checks are local
  renders plus read-only production metrics/resource verification.

## Documentation Impact

- Updated: None
- Generated docs: Not required; architecture activation paths unchanged
- No-docs rationale: Narrow Alloy service discovery fix; existing observability
  topology remains accurate.

## SDD Conformance

- Local sources checked: `docs/runbooks/spec-driven-development.md`,
  `docs/runbooks/implementation-workflow.md`
- Upstream Spec Kit sources checked: N/A
- Spec -> Plan -> Tasks -> Implement alignment: Artifacts created before the
  manifest edit.
- Artifact updates after implementation: completed with implementation path,
  validation results, and exceptions.

## Exceptions And Follow-Ups

- Worktree fallback path used because `/workspaces/homelab-worktrees` was not
  writable.
- After merge, verify Flux applies the change and the Mimir query
  `up{namespace="immich"} == 0` returns no Immich PostgreSQL service targets.

## Final State

- Final branch: `codex/fix-immich-cnpg-scrape`
- Final HEAD: recorded in final handoff after the last evidence amend
- Commit: `fix(alloy): drop cnpg service scrape targets`
