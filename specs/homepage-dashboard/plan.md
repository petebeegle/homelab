# Plan

## Risk Tier

SDD tier: medium

Workflow tier: medium

This changes Kubernetes-rendered application configuration and Flux
substitutions, but does not change controllers, storage classes, secrets, or
production traffic routing.

## Public Repository Changes

- Add `homepage_target_domain` to production and development `cluster-vars`.
- Update `kubernetes/apps/homepage/base/configmap.yaml`:
  - service and bookmark hrefs that target lab services use
    `${homepage_target_domain}`;
  - status-only cards omit `href`;
  - private media/download service names remain absent.
- Preserve Homepage route and allowed-host substitutions based on
  `${cluster_domain}`.
- Update SDD artifacts and evidence.

## Private Repository Changes

- Update the existing private Homepage ConfigMap service hrefs to use
  `${homepage_target_domain}`.
- Keep private media/download service entries in the private repository.
- Record concise non-secret notes or evidence consistent with the private repo's
  existing style if no SDD scaffold exists.

## Validation

- Validate runtime workflow marker, plan, owner attestation, and SDD context in
  the public clone.
- Render public production and development kustomizations.
- Assert development Homepage route stays development-scoped.
- Assert development Homepage href targets use the production target domain.
- Render private production apps.
- Run `python3 tools/architecture/render.py --check`; run `--write` only if
  generated architecture is stale.
- Attempt development validation only if required credentials and cluster access
  are clearly available.

## Risks And Mitigations

- Dev dashboard intentionally links to production services; render assertions
  verify only the dashboard route and allowed hosts stay development scoped.
- Homepage Kubernetes status cards depend on workload labels; cards use known
  namespaces and app names from current manifests.
- Private names must not leak into the public repo; grep checks and review of
  public ConfigMap guard this.
