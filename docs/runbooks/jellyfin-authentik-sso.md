---
status: current
scope:
  - jellyfin
  - authentik
  - sso
last_verified: 2026-05-23
---

# Jellyfin Authentik SSO

Jellyfin web SSO is provided by the 9p4 SSO Authentication plugin, pinned in GitOps to release `v4.0.0.4`. The Authentik setup follows the community integration guide at <https://integrations.goauthentik.io/media/jellyfin/>.

Authentik owns the `jellyfin` OAuth2/OpenID provider and Jellyfin application. The provider name visible to Jellyfin is `authentik`, with client ID `jellyfin`, redirect URL `https://jellyfin.${cluster_domain}/sso/OID/redirect/authentik`, and launch URL `https://jellyfin.${cluster_domain}/sso/OID/start/authentik`.

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
