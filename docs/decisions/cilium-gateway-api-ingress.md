---
id: ADR-0002
status: accepted
scope:
  - kubernetes
  - ingress
  - cilium
authority: binding
created: 2026-05-09
last_verified: 2026-05-14
supersedes: []
superseded_by:
---

# Cilium Gateway API Ingress

## Decision

Use Cilium Gateway API for cluster ingress. Do not add traditional Kubernetes Ingress resources.

## Rationale

- Cilium provides Gateway API support, L2 load balancer IP advertisement, and kube-proxy replacement in one networking layer.
- Gateway API separates shared listener configuration from app-owned routes.
- Existing apps use `HTTPRoute` for Gateway-terminated HTTPS or Cloudflare Tunnel HTTP routing, and `TLSRoute` for passthrough to services that terminate TLS themselves.
- Cilium Gateway routes forward HTTP traffic to `HTTPRoute` backends. Use an explicit in-cluster proxy when an external backend must be contacted over HTTPS but cannot present a certificate trusted for the public hostname.
- Cloudflare Tunnel public hostnames use a dedicated HTTP Gateway so app-owned routes still select the backend Service instead of pointing cloudflared directly at app Services.

## Consequences

- LAN HTTP apps attach to Gateway `internal` in namespace `gateway`, section `https-gateway`.
- WireGuard service-plane HTTP apps attach to Gateway `external` in namespace `gateway`, section `https-gateway`; this is not internet-public exposure.
- Internet-public HTTP apps attach to Gateway `public` in namespace `gateway`, section `http-gateway`, and require a matching cloudflared ingress rule that targets `http://cilium-gateway-public.gateway.svc.cluster.local:80`.
- Hostnames should use `${cluster_domain}` in shared manifests.
- Cilium settings such as `kubeProxyReplacement: true` and L2 announcements are ingress-critical.
- Use `HTTPRoute` when the cluster should provide the trusted certificate, normalize a public hostname, or hide a backend port.
- Use `TLSRoute` passthrough only when the target should terminate TLS itself and presents an acceptable certificate for the hostname. LAN passthrough uses Gateway `passthrough`; WireGuard service-plane passthrough uses Gateway `external-passthrough`.
- TLS passthrough targets terminate TLS themselves and do not need cert-manager certificates. Passthrough route readiness also depends on the route being included in the app Kustomization, DNS outside this repo when applicable, and backend SNI/certificate behavior.

## Operational Notes

- If a Gateway does not receive an IP, check Cilium L2 announcement and IP pool resources.
- If TLS is failing for Gateway-terminated routes, verify cert-manager Certificates and the wildcard Secret.
- If passthrough is failing, verify `TLSRoute` attachment on the target Gateway, DNS to the correct Gateway address, and the backend TLS handshake with the expected SNI.
- Verify routes with `kubectl get httproute -A` or `kubectl get tlsroute -A` and inspect `Accepted` and `Programmed` conditions.
