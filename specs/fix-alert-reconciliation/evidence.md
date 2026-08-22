# Evidence: Fix Alert Reconciliation

## Live Diagnosis

- Production Grafana Kustomization failed strict post-build substitution because `ConfigMap/flux-dashboard` contains the Grafana runtime placeholder `${DS_LOKI}`.
- The failure made `onepassword-items` and several dashboard/app Kustomizations report dependency failures, which fired Flux alerts.
- Production 1Password synchronization is healthy: 17/17 `OnePasswordItem` resources are `Ready=True` and the live operator polling interval is `3600` seconds.
- Private Arr source has a separate unescaped runtime shell variable failure; remediation is pull request 43 in `petebeegle/homelab-private`.

## Validation

- `jq empty kubernetes/infra/monitoring/grafana/dashboards/flux-dashboard.json`: PASS.
- `kubectl kustomize kubernetes/infra/monitoring/grafana` followed by strict Flux substitution with the production `cluster_domain`: PASS; rendered dashboard retains 3 `${DS_LOKI}` and 26 `${DS_PROMETHEUS}` runtime placeholders.
- `python3 tools/architecture/render.py --check`: PASS.
- `git diff --check`: PASS.
- The configured `check-json` pre-commit hook is unavailable; `yamllint` and `k8svalidate` correctly skipped the JSON file.
