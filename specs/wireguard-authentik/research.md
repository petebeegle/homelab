# Research: WireGuard Authentik Gate

## Decision 1: Use Authentik Proxy Mode

**Decision**: Protect `vpn.${cluster_domain}` with an Authentik proxy provider in
proxy mode, served by the embedded proxy outpost, and forward authorized
requests to
`http://wireguard-http.wireguard.svc.cluster.local:51821`.

**Rationale**: The pinned wg-easy 15.3.0 deployment has local initialization and
credential behavior but no documented native OIDC configuration in the current
wg-easy v15 documentation. Authentik proxy mode is designed for an existing web
application: the outpost receives the external request, authenticates and
authorizes it, then forwards to the configured internal host. This keeps
identity enforcement outside wg-easy and does not change its database.

**Alternatives considered**:

- Native wg-easy OIDC: rejected because no supported v15 configuration was
  found and inventing undocumented environment variables is unsafe.
- Gateway forward-auth filter: rejected because this repo has no established
  Cilium/Gateway API external-auth policy and Authentik's documented
  forward-auth examples assume a reverse proxy that implements the auth
  subrequest contract.
- Add a new sidecar reverse proxy: rejected because the embedded Authentik proxy
  already owns this capability with less secret and lifecycle surface.

## Decision 2: Route The Hostname To Authentik

**Decision**: Keep the HTTPRoute in the `wireguard` namespace and its
`gateway/internal` parent, but replace the direct wg-easy backend with
`authentik-server` in namespace `authentik`. Add a target-namespace
ReferenceGrant scoped to the WireGuard HTTPRoute.

**Rationale**: The route remains owned with the app, uses the binding Gateway
API architecture, and preserves the LAN-only exposure. The cross-namespace
ReferenceGrant makes the trust relationship explicit and testable. The
embedded outpost is available through the Authentik server Service and can
select the proxy provider from the `vpn` Host header.

**Alternatives considered**:

- Move the HTTPRoute to the Authentik namespace: rejected because it separates
  the app hostname from the WireGuard desired-state package and reverses the
  cross-namespace trust direction.
- Deploy a dedicated managed outpost: deferred because there are no existing
  proxy providers or scaling/isolation requirements that justify a new
  Deployment, Secret, and Service.
- Keep the direct backend and route only `/outpost.goauthentik.io`: rejected
  because Cilium HTTPRoute does not itself perform Authentik's forward-auth
  subrequest and deny/redirect contract.

## Decision 3: Require A Dedicated Administrator Group

**Decision**: Create a `WireGuard Admins` group and bind it to the Authentik
application while retaining built-in `authentik Admins` as a break-glass path.
Preserve wg-easy's local login and API credential behind the outer gate.

**Rationale**: wg-easy can create, revoke, download, and display VPN client
configuration, so ordinary authenticated homelab membership is too broad. The
built-in admin binding avoids a cutover lockout while the new group is initially
empty. Keeping the inner credential provides defense in depth and preserves
existing machine clients.

**Alternatives considered**:

- Allow every authenticated Authentik user: rejected as excessive privilege.
- Remove wg-easy local authentication: rejected because it increases coupling
  to the proxy, changes API clients, and weakens recovery.
- Send the wg-easy password from Authentik as Basic Auth: rejected because it
  adds secret distribution and removes the intentional second control without
  a demonstrated requirement.

## Decision 4: Preserve Machine-To-Machine Access

**Decision**: Apply Authentik only at the user-facing Gateway hostname. Do not
change `wireguard-http`, the wg-easy workload, or the access-broker's direct
ClusterIP endpoint and credential.

**Rationale**: Browser SSO redirects are inappropriate for automation. The
ClusterIP boundary is already the intended trusted integration path, while the
LAN hostname is the human entry point.

**Alternatives considered**:

- Force access-broker through the Gateway and Authentik: rejected because it
  would require a new non-interactive OAuth client and changes outside the
  stated fix.

## Decision 5: Validation And Development Exception

**Decision**: Add an exact-host unauthenticated Playwright regression, run
production renders and repository checks, then require layered post-reconcile
production verification. Record `smoke_profile: none` for development unless a
safe temporary deployment of both Authentik and VPN becomes available.

**Rationale**: The development base deliberately omits Authentik and VPN. A
whoami-only branch smoke cannot prove the proxy provider, group policy, or
wg-easy upstream. The strongest representative evidence is therefore a
pre-change expected failure, local desired-state validation, production
synthetic smoke, two authorization personas, the existing UDP peer path, and
the direct API path.

**Alternatives considered**:

- Claim Gateway render/readiness as completion: rejected because repository
  policy requires the exact user path for routed changes.
- Add Authentik and VPN permanently to development in this PR: rejected as
  substantial environment and secret scope expansion.

## Separate Routed-App Audit

The user-requested separate read-only audit excluded Valheim and found these
desired-state surfaces without an Authentik application:

| Surface | Exposure | Assessment |
| ------- | -------- | ---------- |
| WireGuard UI | LAN HTTPS | Sensitive admin UI; fix in this implementation |
| Homepage | LAN and WireGuard HTTPS | Network restriction is explicit, but Authentik omission is not; highest-priority follow-up because dashboard/private config can reveal infrastructure details |
| Pi-hole web UI | LAN HTTPS | Native admin password exists; likely intentional, but policy should decide whether native auth is sufficient |
| Whoami | LAN and WireGuard HTTPS | Intentional Gateway diagnostic; review whether permanent header/source disclosure is worth the operational value |
| Foundry VTT | LAN and internet-public HTTPS | Public exposure and native account/admin secrets are intentional; blanket Authentik could break players |
| Access broker callback/download paths | Internet-public HTTPS | Anonymous Discord/OAuth callbacks and tokenized downloads are intentional; blanket Authentik is unsuitable |
| OTLP collector | LAN HTTPS plus LoadBalancer | Authentik is unsuitable for agents, but unauthenticated telemetry and unspecified LoadBalancer placement need a separate network-auth review |

Protocol-only WireGuard UDP, VPN DNS, and Pi-hole DNS use protocol/network
controls and are not browser Authentik candidates. Dormant Proxmox/UniFi routes
are not included by the current production Kustomization. Apps from the
separate `homelab-private` repository were unavailable to this audit.

## Documentation Sources Consulted

- Authentik proxy provider modes:
  `https://docs.goauthentik.io/add-secure-apps/providers/proxy/`
- Authentik proxy provider creation:
  `https://docs.goauthentik.io/add-secure-apps/providers/proxy/create-proxy-provider/`
- Authentik embedded outpost configuration:
  `https://docs.goauthentik.io/add-secure-apps/outposts/embedded/`
- wg-easy v15 documentation:
  `https://wg-easy.github.io/wg-easy/latest/`
