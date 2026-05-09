# Synology NFS Storage

## Status

Accepted.

## Decision

Use Synology-backed NFS through StorageClass `nfs-csi-storage` for persistent Kubernetes app storage.

## Rationale

- Synology NFS provides shared storage for workloads that need persistence.
- The NFS CSI controller integrates storage provisioning with Kubernetes PVCs.
- Btrfs-backed Synology volumes support quota behavior needed by the CSI driver.

## Consequences

- NFS-dependent apps must depend on the `nfs-csi` Flux Kustomization.
- PVC workloads are blocked if Synology CSI is unhealthy.
- NAS NFS exports must allow the node subnet and any local development subnet that needs access.
- UID/GID mismatches must be handled with workload security context or NAS permissions.

## Operational Notes

- StorageClass: `nfs-csi-storage`.
- NAS IP in current production variables: `192.168.30.99`.
- Synology CSI runs in namespace `dataplane`.
- Use NFS v4.1 for RWX volumes.
- Use Btrfs volumes on the NAS; avoid ext4 for CSI quota-backed storage.
