# Cilium Gateway API Ingress

## Status

Accepted.

## Decision

Use Cilium Gateway API for cluster ingress. Do not add traditional Kubernetes Ingress resources.

## Rationale

- Cilium provides Gateway API support, L2 load balancer IP advertisement, and kube-proxy replacement in one networking layer.
- Gateway API separates shared listener configuration from app-owned routes.
- Existing apps use `HTTPRoute` for Gateway-terminated HTTPS and `TLSRoute` for passthrough to external services that terminate TLS themselves.
- Cilium Gateway routes forward HTTP traffic to `HTTPRoute` backends. Use an explicit in-cluster proxy when an external backend must be contacted over HTTPS but cannot present a certificate trusted for the public hostname.

## Consequences

- Internal HTTP apps attach to Gateway `internal` in namespace `gateway`, section `https-gateway`.
- Hostnames should use `${cluster_domain}` in shared manifests.
- Cilium settings such as `kubeProxyReplacement: true` and L2 announcements are ingress-critical.
- Use `HTTPRoute` when the cluster should provide the trusted certificate, normalize a public hostname, or hide a backend port.
- Use `TLSRoute` passthrough only when the target should terminate TLS itself and presents an acceptable certificate for the hostname.
- TLS passthrough targets terminate TLS themselves and do not need cert-manager certificates.

## Operational Notes

- If a Gateway does not receive an IP, check Cilium L2 announcement and IP pool resources.
- If TLS is failing for internal routes, verify cert-manager Certificates and the wildcard Secret.
- Verify routes with `kubectl get httproute -A` or `kubectl get tlsroute -A` and inspect `Accepted` and `Programmed` conditions.
