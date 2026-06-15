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

Production keeps a strict Authentik redirect URL for Jellyfin: `https://jellyfin.lab.petebeegle.com/sso/OID/redirect/authentik`. Development uses a separate Authentik overlay under `kubernetes/clusters/development/overlays/authentik` so branch Jellyfin environments can also use callback URLs such as `https://jellyfin-<slug>.dev.lab.petebeegle.com/sso/OID/redirect/authentik` without widening the production provider.

The Authentik provider must allow the `authorization_code` grant type, with `refresh_token` enabled alongside it for the normal web authorization-code flow. If Authentik redirects back to Jellyfin with `error=invalid_request&error_description=The request is otherwise malformed` and the Authentik server logs show `Invalid grant_type for provider` with `grant_type=authorization_code`, confirm the Jellyfin provider blueprint includes those grant types.

The GitOps bootstrap writes the plugin configuration at `/config/plugins/configurations/SSO-Auth.xml`. For plugin `v4.0.0.4`, each OIDC provider dictionary value must be rooted as `<PluginConfiguration>` inside the `<value>` element. If it is written as `<OidConfig>`, the plugin rewrites `OidConfigs` empty and `/sso/OID/start/authentik` fails with `Provider does not exist`.

Jellyfin sits behind Gateway API TLS termination, so the upstream hop into the pod is HTTP even though the public route is HTTPS. The Authentik provider strictly allows `https://jellyfin.${cluster_domain}/sso/OID/redirect/authentik`; keep the plugin `<SchemeOverride>` set to `https` so Jellyfin generates that redirect URI instead of an `http://` callback.

The bootstrap runs from an init container, so ConfigMap or init script changes require a Jellyfin pod restart before they take effect. The plugin install step is intentionally idempotent for rolling restarts: when the existing `SSO Authentication_4.0.0.4` directory already contains the expected plugin files, the bootstrap reuses it instead of deleting it from the shared config PVC while an older pod may still be serving traffic.

Group membership is exposed through the `groups` OIDC scope and claim. Users must be in `Jellyfin Users` or `Jellyfin Admins` to pass plugin authorization. Members of `Jellyfin Admins` are mapped to Jellyfin administrators.

Native Jellyfin login is intentionally preserved. Keep at least one local administrator or QuickConnect-capable fallback available for native clients and for recovery if Authentik, group claims, or the SSO plugin fail. The plugin does not provide an SSO logout callback; logging out of Jellyfin only ends the Jellyfin session.

## Development Verification

The development cluster includes Authentik for Jellyfin SSO validation. Its overlay uses development-only SOPS secret material and a blueprint fixture that creates user `test`, sources the password from `JELLYFIN_TEST_PASSWORD`, and adds the user to `Jellyfin Users`.

The Jellyfin branch overlay is intentionally CPU-schedulable so SSO and Gateway smoke tests can run on the single-node development cluster even when the production iGPU label and `gpu.intel.com/i915` resource are unavailable. Production Jellyfin still hard-requires the iGPU node selector and device-plugin allocation.

For branch validation, use the Jellyfin branch verifier with the shared-base reconcile because the branch depends on development Authentik:

```bash
python3 tools/development/verify_branch_deploy.py \
  --app jellyfin \
  --branch codex/<implementation> \
  --slug jellyfin-auth-sso \
  --push \
  --include-cluster-base
```

After the automated verifier passes, collect manual evidence from the development cluster:

```bash
kubectl --kubeconfig ~/.kube/homelab-development.config -n flux-system get kustomizations authentik branch-jellyfin-jellyfin-auth-sso
kubectl --kubeconfig ~/.kube/homelab-development.config -n authentik get helmrelease,httproute,pods
kubectl --kubeconfig ~/.kube/homelab-development.config -n jellyfin-jellyfin-auth-sso get helmrelease,httproute,pvc,pods
kubectl --kubeconfig ~/.kube/homelab-development.config -n authentik logs deploy/authentik-worker --tail=100
kubectl --kubeconfig ~/.kube/homelab-development.config -n jellyfin-jellyfin-auth-sso logs deploy/jellyfin-jellyfin-auth-sso --tail=100
```

Then use Playwright or a browser on the LAN to visit `https://jellyfin-jellyfin-auth-sso.dev.lab.petebeegle.com`, click the SSO button, sign in to Authentik with `test` / `test`, and confirm Jellyfin returns to `/sso/OID/redirect/authentik` and creates an authenticated session.

## `invalid_client` Recovery

If Authentik returns `invalid_client`, first compare secret references rather than rotating immediately:

1. Confirm the development Authentik Secret and the Jellyfin branch Secret both render `JELLYFIN_OAUTH_CLIENT_SECRET` from SOPS-encrypted manifests.
2. Confirm the Jellyfin branch init container reads `jellyfin-${branch_slug}-secrets` and the Authentik HelmRelease reads `authentik-secrets`.
3. Reconcile Authentik, then the branch Jellyfin Kustomization, and restart the branch Jellyfin pod so `SSO-Auth.xml` is rewritten from the current secret.
4. Check Authentik worker logs for blueprint import errors and Jellyfin init-container logs for bootstrap failures.

Rotate only the Jellyfin OAuth client secret when the live Authentik provider and branch Jellyfin Secret are proven out of sync or the secret is suspected compromised. When rotating, update all SOPS manifests that carry the same client secret in one change, reconcile Authentik first, then restart/reconcile Jellyfin.

After reconcile, acceptance should confirm:

1. Authentik has the `jellyfin` application and `authentik` OAuth provider.
2. Jellyfin starts with the SSO Authentication plugin installed.
3. The Jellyfin login page shows the SSO button and starts at `/sso/OID/start/authentik`.
4. A `Jellyfin Users` member can sign in.
5. A `Jellyfin Admins` member receives Jellyfin administrator access.
