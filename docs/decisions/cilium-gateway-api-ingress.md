# Cilium Gateway API Ingress

## Status

Accepted.

## Decision

Use Cilium Gateway API for cluster ingress. Do not add traditional Kubernetes Ingress resources.

## Rationale

- Cilium provides Gateway API support, L2 load balancer IP advertisement, and kube-proxy replacement in one networking layer.
- Gateway API separates shared listener configuration from app-owned routes.
- Existing apps use `HTTPRoute` for internal HTTPS and `TLSRoute` for passthrough to external services.

## Consequences

- Internal HTTP apps attach to Gateway `internal` in namespace `gateway`, section `https-gateway`.
- Hostnames should use `${cluster_domain}` in shared manifests.
- Cilium settings such as `kubeProxyReplacement: true` and L2 announcements are ingress-critical.
- TLS passthrough targets terminate TLS themselves and do not need cert-manager certificates.

## Operational Notes

- If a Gateway does not receive an IP, check Cilium L2 announcement and IP pool resources.
- If TLS is failing for internal routes, verify cert-manager Certificates and the wildcard Secret.
- Verify routes with `kubectl get httproute -A` or `kubectl get tlsroute -A` and inspect `Accepted` and `Programmed` conditions.
