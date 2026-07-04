---
status: draft
scope:
  - immich
  - photos
  - authentik
  - storage
  - postgres
authority: operational
created: 2026-07-04
last_verified: 2026-07-04
---

# Immich

Immich runs as a Flux-managed Kubernetes app at
`https://immich.${cluster_domain}`. It is exposed on the LAN internal Gateway
and the WireGuard service-plane external Gateway. It is not internet-public.

## Storage

Uploaded photos and generated media live on PVC `immich-library` in namespace
`immich`, using StorageClass `nfs-csi-media-storage` with an initial request of
`1Ti`.

PostgreSQL data lives in CloudNativePG cluster `immich-postgres` on StorageClass
`local-path`. Do not move the database PVC to NFS. Immich database backups are
metadata-only and must be paired with NAS asset backups for complete recovery.

## Authentication

Production uses Authentik OAuth/OIDC. Native Immich password login is disabled
by GitOps configuration. The Authentik blueprint creates:

- `Immich Users`
- `Immich Admins`
- OAuth provider/application `immich`

Users in `Immich Admins` receive the `immich_role=admin` claim; other OAuth
users receive `immich_role=user`.

## Operations

Useful checks:

```sh
kubectl -n immich get hr,pods,pvc,httproute
kubectl -n immich get cluster.postgresql.cnpg.io immich-postgres
kubectl -n immich logs deploy/immich-server --tail=100
flux debug helmrelease immich -n immich --show-values
```

Grafana dashboard `Immich Overview` is managed by Grafana Operator resources in
the `Immich` folder.

## Recovery Notes

Original photos on the NAS are not enough to restore the Immich application
state. The database stores users, asset records, albums, sharing, face/search
metadata, paths, and job state. Keep database backups and NAS media backups in
sync.
