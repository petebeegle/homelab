# Authentication Preservation Checklist: Jellyfin Local Config

**Purpose**: Make authentication preservation release-blocking for the Jellyfin
config storage migration.
**Created**: 2026-08-08
**Feature**: [spec.md](../spec.md)

## Desired-State Review

- [x] The PR does not edit
      `kubernetes/infra/authentik/blueprints/jellyfin-oauth.yaml`.
- [x] The PR does not edit `kubernetes/apps/jellyfin/secret.yaml`.
- [x] Client ID remains `jellyfin`.
- [x] Provider name remains `authentik`.
- [x] Redirect URI remains
      `https://jellyfin.${cluster_domain}/sso/OID/redirect/authentik`.
- [x] Scope and role claim remain `groups`.
- [x] Authorization groups remain `Jellyfin Users` and `Jellyfin Admins`.
- [x] HTTPS scheme override remains enabled by the existing SSO bootstrap.
- [x] Native Jellyfin login remains enabled.

## Migration Integrity

- [x] The source config PVC is retained and mounted read-only.
- [x] The old Jellyfin process is stopped before copy through `Recreate`.
- [x] All Jellyfin database files under `/config/data` are copied and compared.
- [x] `SSO-Auth.xml`, `branding.xml`, and `system.xml` are copied and compared.
- [x] All expected pinned plugin files are copied and compared.
- [x] The completion marker is written only after validation.
- [x] An unmarked target is replaced rather than trusted.
- [x] A failed migration or SSO bootstrap prevents application startup.

## Cutover Acceptance

- [ ] `/sso/OID/start/authentik` reaches Authentik without
      `Provider does not exist`.
- [ ] The generated callback is HTTPS and exactly matches the strict Authentik
      redirect URI.
- [ ] An existing `Jellyfin Users` member reaches the same Jellyfin account.
- [ ] An existing `Jellyfin Admins` member retains administrator access.
- [ ] A known native local administrator can sign in without Authentik.
- [ ] The old NFS PVC remains present for immediate rollback.
- [ ] The selected iGPU worker has `MemoryPressure=False`.
