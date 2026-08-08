---
id: ADR-0015
status: accepted
scope:
  - jellyfin
  - storage
  - local-path
  - authentication
authority: binding
created: 2026-08-08
last_verified: 2026-08-08
supersedes: []
superseded_by:
---

# Jellyfin Local Config Storage

## Decision

Use the `local-path` StorageClass for Jellyfin's `/config` volume while keeping
media on the existing Synology NFS export.

Migrate the complete existing `jellyfin-config-v2` PVC into a new
`jellyfin-config-local-v1` PVC before Jellyfin starts. The migration source is
mounted read-only, the Deployment uses the `Recreate` strategy, and an init
container validates the copied Jellyfin databases, SSO plugin, SSO
configuration, branding, and system configuration before creating a completion
marker.

The existing NFS PVC remains declared and retained as a point-in-time rollback
source. The Authentik blueprint, OAuth client ID, encrypted client secret,
redirect URI, group names, and native Jellyfin login behavior are not changed by
the storage migration.

This decision is an app-specific exception to the default persistent-app storage
rule in `docs/decisions/synology-nfs-storage.md`.

## Rationale

- Jellyfin performs latency-sensitive SQLite, metadata, and plugin-state I/O
  under `/config` while discovering and ingesting media.
- Those operations currently traverse NFS and compete with media reads and
  Sonarr/Radarr imports on the NAS.
- Node-local storage removes NFS latency from the Jellyfin database and metadata
  path without moving the media library.
- Copying the complete config tree preserves Jellyfin user identities, native
  credentials, permissions, plugins, and SSO state together.
- A fail-closed init sequence is safer than allowing Jellyfin to initialize an
  empty or partially copied config volume.
- `Recreate` prevents two Jellyfin processes from accessing the SQLite state
  during the cutover.

## Constraints

- Jellyfin remains a single replica.
- Jellyfin must continue to select nodes labeled
  `homelab.petebeegle.com/jellyfin-igpu=true`.
- The `local-path-provisioner` Flux Kustomization must be ready before Jellyfin.
- The migration must run before the existing SSO bootstrap init container.
- The migration source must be mounted read-only.
- The migration must validate at least one non-empty Jellyfin database plus the
  pinned SSO plugin and configuration files.
- The main Jellyfin container must not start after a failed migration or failed
  SSO bootstrap.
- Media remains on `/volume1/Media/Jellyfin` through Synology NFS.
- The Jellyfin and migration resource requests do not increase the pod's
  effective scheduling request above the existing 2 GiB application request.
- Production cutover must not proceed while the selected iGPU worker reports
  Kubernetes `MemoryPressure=True`.

## Consequences

- The config volume becomes node-affine. Jellyfin cannot automatically move to
  another worker after the local PVC binds.
- A failed or unavailable bound worker can make Jellyfin unavailable until the
  node returns, the local volume is recovered, or the workload is deliberately
  rolled back to the retained NFS PVC.
- The retained NFS PVC becomes stale after cutover. It is suitable for immediate
  rollback, but later rollback can lose settings, users, and metadata created
  after migration.
- Backups of the local config volume require an explicit host-level or
  application-level strategy; Synology snapshots no longer protect live
  `/config`.
- The media library and therefore normal playback remain dependent on Synology
  availability.
- Authentication acceptance is release-blocking: existing SSO users, admin
  mapping, and native administrator recovery must be verified during cutover.
