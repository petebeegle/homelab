---
id: ADR-0008
status: accepted
scope:
  - synology
  - ingress
  - gateway-api
authority: binding
created: 2026-05-10
last_verified: 2026-05-10
supersedes: []
superseded_by:
---

# Synology Gateway-Terminated HTTPS

## Decision

Expose Synology DSM at `synology.petebeegle.com` through the Cilium internal Gateway with Gateway-terminated HTTPS. The Gateway presents a cert-manager certificate for `synology.petebeegle.com` and sends HTTP to an in-cluster nginx proxy, which then proxies DSM over HTTPS to the NAS on port 5001.

## Rationale

- DSM's built-in certificate for `192.168.30.99:5001` is not trusted for `synology.petebeegle.com`.
- Cilium Gateway does not originate HTTPS upstream just because a Service port advertises `appProtocol: https`.
- DSM's HTTP port redirects browsers to `:5001`, which exposes the backend port if the Gateway proxies to port 5000 directly.
- Gateway termination lets cert-manager issue and renew the public hostname certificate.
- Users should access DSM without a visible backend port.
- Authentik and DSM SSO should use the same public URL.

## Consequences

- DNS for `synology.petebeegle.com` must point at the internal Gateway IP, not directly at the NAS.
- Synology uses an `HTTPRoute` to the internal Gateway instead of a `TLSRoute` to the passthrough Gateway.
- The Synology route targets `synology-proxy`, not DSM directly. The proxy connects to `https://192.168.30.99:5001`, accepts DSM's internal certificate, and rewrites DSM responses that include `https://synology.petebeegle.com:5001` or `https://192.168.30.99:5001`.
- Use `HTTPRoute` for external services when the cluster should provide the trusted certificate or hide backend ports.
- Use `TLSRoute` passthrough only when the external target should terminate TLS itself and presents an acceptable certificate for the hostname.
