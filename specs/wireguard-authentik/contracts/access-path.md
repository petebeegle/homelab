# Access Contract: WireGuard Administration

## Human Browser Contract

**Entry point**: `https://vpn.${cluster_domain}/`

- The hostname is available only through the existing LAN internal Gateway.
- A request without a valid Authentik session must not reach wg-easy content.
- Authentik starts its normal login flow and returns only users authorized by
  the `WireGuard Admins` or built-in `authentik Admins` application bindings.
- An authenticated user in neither group receives an Authentik denial.
- An authorized user is proxied to wg-easy and still completes wg-easy's local
  authentication.
- If Authentik or its proxy provider cannot authorize the request, the path
  fails closed. There is no direct Gateway fallback backend.

Representative unauthenticated paths:

- `/`
- One non-mutating wg-easy API path selected during task design based on the
  pinned v15 behavior

## Machine Client Contract

**Entry point**:
`http://wireguard-http.wireguard.svc.cluster.local:51821`

- Trusted in-cluster clients continue to use the existing wg-easy
  authentication.
- They do not follow browser SSO redirects and do not depend on an Authentik
  session.
- No Service name, port, or credential key changes in this implementation.

## WireGuard Data-Plane Contract

**Entry point**: existing `Service/wireguard` UDP port 30000

- Existing peers, keys, DNS defaults, AllowedIPs, and tunnel behavior are
  unchanged.
- The Authentik gate applies only to HTTP traffic for the administration
  hostname.

## Observable Failure Contract

| Failure | Expected observation |
| ------- | -------------------- |
| No Authentik session | Redirect or Authentik login response; no wg-easy shell |
| Authenticated user in neither authorized group | Authentik authorization denial |
| Authentik unavailable | Closed/failed request; never direct wg-easy fallback |
| Cross-namespace reference invalid | HTTPRoute `ResolvedRefs=False`; rollout is not accepted |
| wg-easy unavailable after authorization | Authentik proxy returns upstream failure; route does not bypass the gate |
