---
id: ADR-0005
status: accepted
scope:
  - storage
  - synology
  - nfs
authority: binding
created: 2026-05-09
last_verified: 2026-05-17
supersedes: []
superseded_by:
---

# Synology NFS Storage

## Decision

Use Synology-backed NFS through dedicated NFS CSI StorageClasses for persistent Kubernetes app storage:

- `nfs-csi-storage` is the default StorageClass for general Homelab app storage on `/volume2/Homelab`.
- `nfs-csi-media-storage` is the opt-in StorageClass for media and download payloads on `/volume1/Media`.

## Rationale

- Synology NFS provides shared storage for workloads that need persistence.
- The NFS CSI controller integrates storage provisioning with Kubernetes PVCs.
- Btrfs-backed Synology volumes support quota behavior needed by the CSI driver.

## Consequences

- NFS-dependent apps must depend on the `nfs-csi` Flux Kustomization.
- PVCs should use `nfs-csi-storage` unless they intentionally store media or download payloads on `nfs-csi-media-storage`.
- PVC workloads are blocked if Synology CSI is unhealthy.
- NAS NFS exports must allow the node subnet and any local development subnet that needs access.
- UID/GID mismatches must be handled with workload security context or NAS permissions.

## Operational Notes

- Default app StorageClass: `nfs-csi-storage`, backed by `/volume2/Homelab`.
- Media/download StorageClass: `nfs-csi-media-storage`, backed by `/volume1/Media`.
- NAS IP in current production variables: `192.168.30.99`.
- Synology CSI runs in namespace `dataplane`.
- Use NFS v4.1 for RWX volumes.
- Use Btrfs volumes on the NAS; avoid ext4 for CSI quota-backed storage.
