---
status: current
scope:
  - jellyfin
  - authentik
  - sso
last_verified: 2026-08-08
---

# Jellyfin Authentik SSO

Jellyfin web SSO is provided by the 9p4 SSO Authentication plugin, pinned in GitOps to release `v4.0.0.4`. The Authentik setup follows the community integration guide at <https://integrations.goauthentik.io/media/jellyfin/>.

Authentik owns the `jellyfin` OAuth2/OpenID provider and Jellyfin application. The provider name visible to Jellyfin is `authentik`, with client ID `jellyfin`, redirect URL `https://jellyfin.${cluster_domain}/sso/OID/redirect/authentik`, and launch URL `https://jellyfin.${cluster_domain}/sso/OID/start/authentik`.

The Authentik provider must allow the `authorization_code` grant type, with `refresh_token` enabled alongside it for the normal web authorization-code flow. If Authentik redirects back to Jellyfin with `error=invalid_request&error_description=The request is otherwise malformed` and the Authentik server logs show `Invalid grant_type for provider` with `grant_type=authorization_code`, confirm the Jellyfin provider blueprint includes those grant types.

The GitOps bootstrap writes the plugin configuration at `/config/plugins/configurations/SSO-Auth.xml`. For plugin `v4.0.0.4`, each OIDC provider dictionary value must be rooted as `<PluginConfiguration>` inside the `<value>` element. If it is written as `<OidConfig>`, the plugin rewrites `OidConfigs` empty and `/sso/OID/start/authentik` fails with `Provider does not exist`.

Jellyfin sits behind Gateway API TLS termination, so the upstream hop into the pod is HTTP even though the public route is HTTPS. The Authentik provider strictly allows `https://jellyfin.${cluster_domain}/sso/OID/redirect/authentik`; keep the plugin `<SchemeOverride>` set to `https` so Jellyfin generates that redirect URI instead of an `http://` callback.

The bootstrap runs from an init container, so ConfigMap or init script changes require a Jellyfin pod restart before they take effect. The plugin install step is intentionally idempotent for rolling restarts: when the existing `SSO Authentication_4.0.0.4` directory already contains the expected plugin files, the bootstrap reuses it instead of deleting it from the shared config PVC while an older pod may still be serving traffic.

Group membership is exposed through the `groups` OIDC scope and claim. Users must be in `Jellyfin Users` or `Jellyfin Admins` to pass plugin authorization. Members of `Jellyfin Admins` are mapped to Jellyfin administrators.

Native Jellyfin login is intentionally preserved. Keep at least one local administrator or QuickConnect-capable fallback available for native clients and for recovery if Authentik, group claims, or the SSO plugin fail. The plugin does not provide an SSO logout callback; logging out of Jellyfin only ends the Jellyfin session.

After reconcile, acceptance should confirm:

1. Authentik has the `jellyfin` application and `authentik` OAuth provider.
2. Jellyfin starts with the SSO Authentication plugin installed.
3. The Jellyfin login page shows the SSO button and starts at `/sso/OID/start/authentik`.
4. A `Jellyfin Users` member can sign in.
5. A `Jellyfin Admins` member receives Jellyfin administrator access.

## Local Config Storage Migration

Jellyfin's live `/config` volume is migrated from the retained
`jellyfin-config-v2` NFS PVC to `jellyfin-config-local-v1` on `local-path`.
Media remains on Synology NFS. The storage decision and its availability
tradeoffs are documented in
`docs/decisions/jellyfin-local-config-storage.md`.

The Deployment uses `Recreate`. The `migrate-config` init container runs before
`install-sso-auth`, copies the complete config tree from the read-only NFS source,
validates the copied databases and authentication artifacts, and only then
creates `.homelab-config-migration-v1`. A target without that marker is treated
as incomplete and replaced from the source. Either init-container failure blocks
the Jellyfin container from starting.

Before merge or manual reconciliation:

1. Confirm `jellyfin-config-v2` is `Bound`.
2. Confirm both iGPU workers have `MemoryPressure=False`.
3. Confirm the intended worker and its Proxmox host have safe memory headroom.
4. Confirm a native local administrator credential is available.
5. Confirm the encrypted `JELLYFIN_OAUTH_CLIENT_SECRET` and Authentik blueprint
   are unchanged in the diff.
6. Confirm the old NFS PVC will remain declared after cutover.

Authentication is a release-blocking acceptance gate. Do not consider the
migration complete from pod readiness or the login page alone. Verify:

1. `/sso/OID/start/authentik` redirects to the Authentik authorization endpoint
   without `Provider does not exist`.
2. The callback remains
   `https://jellyfin.${cluster_domain}/sso/OID/redirect/authentik`.
3. An existing `Jellyfin Users` member reaches the same existing Jellyfin user.
4. An existing `Jellyfin Admins` member retains Jellyfin administrator access.
5. A native local administrator can still sign in without Authentik.
6. The old NFS PVC remains present for immediate rollback.

For immediate rollback, point `persistence.config.existingClaim` back to
`jellyfin-config-v2`, remove or disable the migration init container, and
reconcile through Flux. The retained source is a point-in-time copy; after the
local volume has been in service, rollback can lose changes made since the
migration.
