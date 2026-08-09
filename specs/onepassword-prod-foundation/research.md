# Research: onepassword-prod-foundation

## Reuse the shared operator manifests

**Decision**: Production references `kubernetes/infra/controllers/onepassword-operator`, identical to development.

**Rationale**: Phase 1 proved chart 2.4.1/operator 1.12.0, direct service-account authentication, Connect disabled, sync, rotation, and auto-restart. A cluster-specific copy would create drift.

## Production bootstrap isolation

**Decision**: Set production Terraform to `dual` and add a validated non-secret reference default of `op://cluster bootstrap/onepassword-production-operator/credential`.

**Rationale**: The shared helper already guarantees protected temporary-file handling and preserves `sops-age`. Separate item and service-account identities prevent cross-cluster token reuse.

## Item readiness metrics

**Decision**: Extend the existing kube-state-metrics custom-resource configuration for `onepassword.com/v1, OnePasswordItem`, exporting only name, namespace, and Ready status in `onepassword_item_info`.

**Rationale**: The repository already uses this pattern for Flux resources. It avoids application data and gives Grafana a stable signal for missing/non-True readiness.

## Alert placement

**Decision**: Add a dedicated Grafana alert group in the existing production monitoring stack. Alert on an absent/unavailable operator Deployment and any item whose Ready label is not `True`, both for ten minutes.

**Rationale**: Dedicated rules make the ownership and runbooks clear. Treating an absent Deployment explicitly avoids a false healthy result caused by `OR vector(0)`.

## Canary reuse

**Decision**: Reuse `tools/development/verify_onepassword_operator.py` and its temporary manifests, supplying production vault, item, kubeconfig, and slug parameters.

**Rationale**: The verifier is already tested, cluster-agnostic, metadata-only, cleanup-safe, and proved in development. Production-specific duplication would increase secret-handling risk.
