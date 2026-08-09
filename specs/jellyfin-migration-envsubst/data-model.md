# Data Model: Jellyfin Migration Rendering

## Source script

- **Path**: `kubernetes/apps/jellyfin/migrate-config.sh`
- **Owner**: POSIX shell at init-container runtime
- **Invariant**: Shell parameter expressions remain literal during GitOps
  rendering.

## Generated ConfigMap

- **Name**: `jellyfin-config-migration`
- **Namespace**: `jellyfin`
- **Key**: `migrate.sh`
- **Generator**: `kubernetes/apps/jellyfin/kustomization.yaml`
- **Flux policy**: `kustomize.toolkit.fluxcd.io/substitute: disabled`
- **Invariant**: `data["migrate.sh"]` equals the source script byte for byte.

## Runtime consumer

- **Consumer**: Jellyfin migration init container
- **Mount**: Generated script ConfigMap
- **Inputs**: Read-only NFS source PVC and local target PVC
- **State transition**: Unmigrated target -> validated copied state -> marker;
  marker-present retries validate the target and do not require the source.

## Unchanged neighboring resource

- **Name**: `jellyfin-values`
- **Flux policy**: Substitution remains enabled.
- **Invariant**: Cluster-domain and other intended GitOps variables continue to
  resolve normally.
