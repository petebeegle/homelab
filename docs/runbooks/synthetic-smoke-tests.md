# Synthetic Smoke Tests

Use this runbook when the in-cluster Playwright smoke checks fail or when adding a routed app to the smoke suite.

## Purpose

`CronJob/synthetic-smoke` runs in the `synthetics` namespace and validates user-visible routes from inside the cluster. These checks exercise DNS, Gateway API routing, TLS termination, HTTP redirects, and the first unauthenticated page shell for selected apps.

The checks are intentionally deeper than pod readiness and lighter than full authenticated end-to-end tests. They do not use credentials in v1.

## Targets

- `whoami.${cluster_domain}` verifies the baseline Gateway TLS path.
- `authentik.${cluster_domain}` verifies the SSO start or login page.
- `monitoring.${cluster_domain}` verifies the Grafana login or landing shell.
- `jellyfin.${cluster_domain}` verifies the Jellyfin web shell.
- `pihole.${cluster_domain}` verifies the root redirect to `/admin`.
- `foundry.${cluster_domain}` verifies the Foundry application shell.

## Manual Run

Create a one-off Job from the CronJob:

```bash
kubectl create job -n synthetics synthetic-smoke-manual-$(date +%Y%m%d%H%M%S) \
  --from=cronjob/synthetic-smoke
```

Watch it finish:

```bash
kubectl get jobs,pods -n synthetics -l app.kubernetes.io/name=synthetic-smoke
```

Read the Playwright output:

```bash
kubectl logs -n synthetics -l app.kubernetes.io/name=synthetic-smoke --tail=200
```

## Common Failures

- DNS failure: confirm the hostname resolves from a pod in `synthetics`.
- TLS failure: check the Gateway certificate and cert-manager Certificate status.
- HTTP 404 or 503: inspect the app `HTTPRoute` Accepted and ResolvedRefs conditions.
- HTTP 5xx: check the backend Service, endpoints, pods, and app logs.
- Missing text or selector: confirm whether the app upgraded or changed its unauthenticated page shell.
- Dependency install failure: check outbound network access from the cluster; the Playwright image is pinned, and the npm dependencies are pinned by `tests/smoke/package-lock.json`.

## Add A Probe

1. Add the routed app to `tests/smoke/routes.spec.js`.
2. Prefer unauthenticated page-shell checks that prove the user-facing route works without storing secrets.
3. Match durable text, titles, or redirects instead of brittle CSS classes.
4. Mirror the same smoke files under `kubernetes/apps/synthetics/smoke/`; Flux cannot load ConfigMap files from outside the app kustomization root.
5. Avoid raw `${...}` syntax in mirrored smoke files unless Flux should substitute it; Flux post-build substitution scans the generated ConfigMap data.
6. Add the app Flux Kustomization to `app-synthetics` `dependsOn` when the probe requires that app to exist first.
7. Run the suite locally when the route is reachable, then create a manual Job after Flux applies the change.

## Dashboard And Alert

Grafana owns the `Synthetics` folder, `Synthetic Smoke` dashboard, and `synthetics` alert rule group. The dashboard shows recent pass/fail counts, Job duration, pod termination reasons, and Loki log excerpts for `namespace="synthetics"`.

The alert fires only when smoke Jobs fail more than once in the last hour. A single failed run should be investigated, but it is not enough to alert by itself.
