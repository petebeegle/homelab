# Data Model: onepassword-prod-foundation

## Production bootstrap identity

- Non-secret reference: `op://cluster bootstrap/onepassword-production-operator/credential`
- Kubernetes Secret identity: `onepassword-system/onepassword-service-account-token`
- Vault scope: read-only `cluster production`
- Invariant: production and development service-account tokens are distinct

## Production operator reconciliation

- Flux Kustomization: `flux-system/onepassword-operator`
- Source path: `./kubernetes/infra/controllers/onepassword-operator`
- Dependency: `flux-system/crds`
- HelmRelease: `onepassword-system/onepassword-operator`
- Runtime: one direct-auth operator replica; no Connect workload

## Item readiness metric

- Source: `onepassword.com/v1 OnePasswordItem`
- Metric: `onepassword_item_info`
- Labels: item name, exported namespace, Ready status
- Excluded: vault/item contents, generated Secret keys, generated Secret bytes

## Alerts

- `onepassword-operator-unavailable`: operator Deployment absent or available replicas below desired for ten minutes
- `onepassword-item-unready`: one or more items have Ready other than `True` for ten minutes
- Evaluation errors are visible; neither alert reads Secret values

## Disposable canary

- Vault: `cluster production`
- Item title: `k8s--onepassword-system--canary`
- Namespace: `onepassword-canary-onepassword-prod-foundation`
- Lifecycle: temporary; default cleanup deletes only this namespace and its generated Secret
