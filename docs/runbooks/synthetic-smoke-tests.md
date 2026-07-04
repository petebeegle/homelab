# Synthetic Smoke Tests

Use this runbook when the in-cluster Playwright smoke checks fail or when adding a routed app to the smoke suite.

## Purpose

`CronJob/synthetic-smoke` runs in the `synthetics` namespace and validates user-visible routes from inside the cluster. These checks exercise DNS, Gateway API routing, TLS termination, HTTP redirects, and the first unauthenticated page shell for selected apps.

The checks are intentionally deeper than pod readiness and lighter than full authenticated end-to-end tests. They do not use credentials in v1.

## Targets

- `whoami.${cluster_domain}` verifies the baseline Gateway TLS path.
- `${cluster_domain}` verifies the Homepage dashboard route at the root lab domain.
- `authentik.${cluster_domain}` verifies the SSO start or login page.
- `monitoring.${cluster_domain}` verifies the Grafana login or landing shell.
- `jellyfin.${cluster_domain}` verifies the Jellyfin web shell.
- `pihole.${cluster_domain}` verifies the root redirect reaches the Pi-hole admin/login shell.
- `foundry.${cluster_domain}` verifies the Foundry application shell.

## Manual Run

Source the opt-in cluster aliases before running manual smoke commands. These
helpers keep the kubeconfig selection scoped to each command process, which is
useful when Codex or an operator needs an explicit cluster context:

```bash
. scripts/kube-aliases.sh
kp config current-context
```

`kd` and `fd` target the development kubeconfig. `kp` and `fp` target the
production kubeconfig. Use `kd config current-context` or
`kp config current-context` before smoke work when the active cluster is
ambiguous.

Production is the default target for the scheduled `synthetic-smoke` CronJob.
Create a one-off Job from the production CronJob:

```bash
kp create job -n synthetics synthetic-smoke-manual-$(date +%Y%m%d%H%M%S) \
  --from=cronjob/synthetic-smoke
```

Watch it finish:

```bash
kp get jobs,pods -n synthetics -l app.kubernetes.io/name=synthetic-smoke
```

Read the Playwright output:

```bash
kp logs -n synthetics -l app.kubernetes.io/name=synthetic-smoke --tail=200
```

When running development-cluster smoke checks instead, use `kd` for Kubernetes
commands and `fd` for Flux commands so the development kubeconfig is selected
without changing the shell's active `KUBECONFIG`.

Every completed run should emit exactly one bounded summary line:

```text
SMOKE_RUN_SUMMARY run="synthetic-smoke-28925520" status=success failed_count=0 failed_tests="" duration_seconds=37
```

Failed runs use `status=failed` and include the final failed Playwright test names after retries in `failed_tests`. The `run` field is the Kubernetes Job name when available, then the pod hostname, then `unknown`. If Playwright fails before the custom reporter can run, the wrapper emits a fallback `SMOKE_RUN_SUMMARY run="..." status=failed` line and preserves the non-zero process exit.

## Common Failures

- DNS failure: confirm the hostname resolves from a pod in `synthetics`.
- TLS failure: check the Gateway certificate and cert-manager Certificate status.
- HTTP 404 or 503: inspect the app `HTTPRoute` Accepted and ResolvedRefs conditions.
- HTTP 5xx: check the backend Service, endpoints, pods, and app logs.
- Missing text or selector: confirm whether the app upgraded or changed its unauthenticated page shell.
- Dependency install failure: check outbound network access from the cluster; the Playwright image is pinned, and the npm dependencies are pinned by `tests/smoke/package-lock.json`.

Find recent final failed test names in Loki:

```logql
{namespace="synthetics", app="synthetic-smoke"} |= "SMOKE_RUN_SUMMARY" | logfmt | status="failed"
```

Group recent failures by final failed test text:

```logql
sum by (failed_tests) (count_over_time({namespace="synthetics", app="synthetic-smoke"} |= "SMOKE_RUN_SUMMARY" | logfmt | status="failed" [1h]))
```

## Add A Probe

1. Add the routed app to `tests/smoke/routes.spec.js`.
2. Prefer unauthenticated page-shell checks that prove the user-facing route works without storing secrets.
3. Match durable text, titles, or redirects instead of brittle CSS classes.
4. Mirror the shared smoke files under `kubernetes/apps/synthetics/smoke/`; Flux cannot load ConfigMap files from outside the app kustomization root.
5. Keep `tests/smoke/routes.spec.js` exactly equal to `kubernetes/apps/synthetics/smoke/routes.spec.js`, and keep the two `package-lock.json` files exactly equal. The `synthetic-smoke-mirroring` pre-commit hook enforces these mirrored pairs.
6. Do not force exact equality for cluster-only wrapper or reporter files, `package.json`, or `playwright.config.js`; those files intentionally differ for the in-cluster runner.
7. Avoid raw `${...}` syntax in mirrored smoke files unless Flux should substitute it; Flux post-build substitution scans the generated ConfigMap data.
8. Add the app Flux Kustomization to `app-synthetics` `dependsOn` when the probe requires that app to exist first.
9. Run `python3 tools/policy/check_synthetic_smoke_mirroring.py` or `pre-commit run synthetic-smoke-mirroring --all-files`, run the suite locally when the route is reachable, then create a manual Job after Flux applies the change.

## Dashboard And Alert

Grafana owns the `Synthetics` folder, `Synthetic Smoke` dashboard, and `synthetics` alert rule group. The dashboard derives smoke run status from Loki `SMOKE_RUN_SUMMARY` lines for `namespace="synthetics", app="synthetic-smoke"`:

- `Recent Status` counts recent `status=failed` summary lines.
- `Smoke Runs` counts `status=success` and `status=failed` summary lines over the panel interval.
- `Job Duration` unwraps `duration_seconds` from the summary line and labels each series by `run`.
- `Smoke Logs` includes `SMOKE_RUN_SUMMARY` lines alongside Playwright failure output.

The alert fires only when summary lines report more than one failed run in the last hour. A single failed run should be investigated, but it is not enough to alert by itself. The alert intentionally remains one aggregate alert instance; it does not group by `failed_tests`, because grouping that label in the alert condition would create separate alert instances per failed test text. Use the failed-test LogQL above from Grafana Explore when the aggregate alert fires.

Failed `synthetic-smoke-*` pods in the `synthetics` namespace are excluded from the generic `Kubernetes Failed Pods` alert because repeated synthetic failures are covered by `Synthetic Smoke Repeated Failures`.
