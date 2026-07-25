# Data Model: WireGuard Authentik Gate

This change adds no application database schema. The durable entities are
declarative identity and routing objects.

## Authentik Group: WireGuard Admins

| Field | Value / rule |
| ----- | ------------ |
| Name | `WireGuard Admins` |
| Purpose | Operators allowed to reach the wg-easy administration surface |
| Membership | Explicit human assignment by an existing Authentik administrator |
| Default | No ordinary Authentik user is implicitly included; built-in `authentik Admins` retain break-glass access |

## Authentik Proxy Provider

| Field | Value / rule |
| ----- | ------------ |
| Stable name | `wireguard-proxy` |
| Mode | Proxy |
| External host | `https://vpn.${cluster_domain}` |
| Internal host | `http://wireguard-http.wireguard.svc.cluster.local:51821` |
| Authorization flow | Existing default provider authorization flow |
| Invalidation flow | Existing default invalidation flow |
| Upstream TLS validation | Not applicable to the HTTP ClusterIP upstream |

## Authentik Application

| Field | Value / rule |
| ----- | ------------ |
| Name | `WireGuard` |
| Slug | `wireguard` |
| Provider | `wireguard-proxy` |
| Launch URL | `https://vpn.${cluster_domain}` |
| Authorization | Policy bindings allow `WireGuard Admins` or built-in `authentik Admins`; all other authenticated users are denied |

## Embedded Outpost Assignment

| Field | Value / rule |
| ----- | ------------ |
| Outpost | Existing `authentik Embedded Outpost` |
| Provider membership | Includes `wireguard-proxy` and every other Git-managed proxy provider, if any are discovered before implementation |
| Service endpoint | Existing `authentik-server` Service used by the Gateway backend |

## Gateway HTTPRoute

| Field | Value / rule |
| ----- | ------------ |
| Name / namespace | `wireguard-ui` / `wireguard` |
| Hostname | `vpn.${cluster_domain}` |
| Parent | `gateway/internal`, section `https-gateway` |
| Backend | `authentik/authentik-server:80` |
| Trust grant | Authentik-namespace ReferenceGrant allowing `wireguard` HTTPRoutes to reference only `authentik-server`; the API cannot scope the source by route name |

## Existing Objects Preserved

- `Service/wireguard` continues to expose UDP port 30000.
- `Service/wireguard-http` remains a ClusterIP for the proxy upstream and
  trusted automation.
- `PersistentVolumeClaim/wireguard-pvc` and wg-easy database rows are unchanged.
- Existing SOPS secrets and access-broker credentials are unchanged.

## Access State Transitions

```text
No Authentik session
  -> Authentik login
  -> authenticated, in neither authorized group -> denied
  -> authenticated, in WireGuard Admins or authentik Admins -> proxied to wg-easy
  -> wg-easy local authentication -> administration UI

Authentik unavailable
  -> fail closed; no direct Gateway fallback to wg-easy

Trusted in-cluster API client
  -> wireguard-http ClusterIP
  -> existing wg-easy authentication
  -> supported API response
```
