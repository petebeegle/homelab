---
status: current
scope:
  - home-assistant
  - authentik
  - sso
last_verified: 2026-07-03
---

# Home Assistant

Home Assistant runs as a declarative Kubernetes app from `ghcr.io/home-assistant/home-assistant:2026.7.0`. Its writable `/config` directory is backed by the `home-assistant-config` PVC on `nfs-csi-storage`; Git-owned YAML files are mounted over the runtime config files from ConfigMaps. Do not commit runtime `.storage` state.

The production app uses Authentik OIDC through `christiaangoossens/hass-oidc-auth` pinned to `v1.1.1`, installed by the pod init container into `/config/custom_components/auth_oidc`. The Authentik blueprint creates `Home Assistant Users`, `Home Assistant Admins`, the public `home-assistant` OAuth2/OIDC provider, and the strict redirect URI `https://homeassistant.${cluster_domain}/auth/oidc/callback`.

`auth_oidc` is configured in `configuration.yaml` with `default_redirect: true` and `force_https: true`. The native `homeassistant` auth provider stays enabled as a recovery login. To use that fallback while default redirect is enabled, open `https://homeassistant.${cluster_domain}/?skip_oidc_redirect=true`.

The GitOps config seeds `/config/.storage/onboarding` with the Home Assistant onboarding steps marked complete so fresh PVCs do not expose `/onboarding.html`. No local Home Assistant credential is created by GitOps; the native `homeassistant` provider remains a recovery path only after an owner creates a local user or password later. With onboarding complete and `auth_oidc` default redirect enabled, the first OIDC-created user should become owner automatically through Home Assistant's empty-user ownership behavior.

Home Assistant is exposed on the LAN and WireGuard service plane through `gateway/internal` and `gateway/external` on `https-gateway`. It is intentionally not added to Cloudflare Tunnel or the public Gateway.

The development branch profile deploys the same container, onboarding storage seed, storage, service, and route shape without the OIDC custom component or Authentik config because the development cluster does not run Authentik. Branch smoke proves the workload, PVC, Service, HTTPRoute, and local Home Assistant shell only; it should not accept first-run onboarding as healthy.

Initial device onboarding remains UI-driven. Pair Elgato, UniFi, and similar integrations through the Home Assistant UI first; add code-owned automations, scripts, scenes, and package YAML after entity IDs are known.

Philips Hue V2 is a runtime config-flow integration, not a declarative Git-owned integration. Pair the Hue bridge through the Home Assistant UI while the bridge link button is available; Home Assistant stores the resulting config entry and tokens under `/config/.storage` on the `home-assistant-config` PVC. Do not commit Hue `.storage` files, `config_entries`, bridge credentials, access or refresh tokens, or fake integration YAML. Do not add an empty `hue.yaml` package as a placeholder.

After pairing, record the runtime inventory before adding Git-owned Hue packages or automations: bridge name, light entity IDs, room/zone/grouped-light entities, scenes, remotes or switches, and any disabled grouped-light entities worth enabling. Once those entity IDs exist, add packages, scripts, scenes, or automations in Git against the observed IDs and keep credentials on the PVC.

Upstream references:

- `hass-oidc-auth` YAML configuration: <https://github.com/christiaangoossens/hass-oidc-auth/blob/main/docs/configuration.md>
- `hass-oidc-auth` Authentik guide: <https://github.com/christiaangoossens/hass-oidc-auth/blob/main/docs/provider-configurations/authentik.md>
- Home Assistant auth providers: <https://www.home-assistant.io/docs/authentication/providers/>
- Home Assistant HTTP reverse-proxy settings: <https://www.home-assistant.io/integrations/http/>

After reconcile, acceptance should confirm:

1. The PVC is Bound with `nfs-csi-storage`.
2. The pod starts with `/config/custom_components/auth_oidc` installed.
3. `https://homeassistant.${cluster_domain}` does not serve `/onboarding.html` and reaches the OIDC welcome or Authentik login flow.
4. A `Home Assistant Users` member can sign in.
5. A `Home Assistant Admins` member receives administrator access.
6. `/?skip_oidc_redirect=true` still exposes the local Home Assistant fallback login once an owner has created local recovery credentials.
