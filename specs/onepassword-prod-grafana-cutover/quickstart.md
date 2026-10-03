# Quickstart: Production Grafana Credential Cutover

## Before Merge

1. Confirm `grafana-credentials-onepassword` reports Ready=True.
2. Run the no-output parity validator and require the `grafana-credentials` pair to pass.
3. Render the production entrypoint strictly and run policy, schema, architecture, harness, and pre-commit checks.
4. Confirm the diff changes only the four Grafana credential references plus policy/tests and SDD artifacts.
5. Confirm the existing production Grafana synthetic route check is healthy.

## After Merge

1. Record the merge SHA and reconcile the production Flux source and Grafana Kustomization.
2. Confirm Flux fetched and applied the merge SHA.
3. Confirm the Grafana HelmRelease, Deployment, Pod, HTTPRoute, Grafana external resource, and managed dashboards/data sources are healthy.
4. Confirm the live Helm and Grafana external resource reference `grafana-credentials-onepassword`, while `envFromSecret` remains `grafana-env`.
5. Run an unauthenticated `/api/health` check and confirm the production synthetic Grafana route check remains healthy.

## Manual Smoke

1. Open `https://monitoring.lab.petebeegle.com`.
2. Select the existing Authentik login path and complete authentication.
3. Open a known dashboard such as the monitoring radar or Kubernetes dashboard.
4. Change the time range or refresh once and confirm panels show current data without data-source errors.
5. Report success or the exact failing layer without sharing credentials or screenshots containing sensitive data.

## Rollback

If any automated or manual acceptance check fails, revert the Grafana cutover commit, merge the revert, reconcile the production Grafana Kustomization, and require the workload and prior login path to recover. Do not delete either Secret or the `OnePasswordItem`.
