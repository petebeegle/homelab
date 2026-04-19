# Networking — Cilium + Gateway API

## Tool priority

Use `kubernetes` MCP for all resource inspection. Fall back to CLI only for Cilium connectivity tests that MCP can't produce.

## Common issues

- **Gateway not getting IP:** Check `l2announcements.enabled: true` in Cilium HelmRelease values
- **TLS not working:** Verify cert-manager Certificates are Ready (`kubectl get cert -A`)
- **Source IP not preserved:** Cilium handles this automatically — no `externalTrafficPolicy` needed
- **CNI change post-deployment:** Causes major disruption — avoid unless necessary
- **kubeProxyReplacement:** Must be `true` for Gateway API to work

## Exposing an internal service (HTTPRoute)

1. Confirm the Service exists with the correct port
2. Create `httproute.yaml` referencing Gateway `internal` in namespace `gateway`, section `https-gateway`
3. Hostname pattern: `<app>.lab.petebeegle.com`
4. Verify: `kubectl get httproute <name> -o yaml` shows `Accepted` + `Programmed`

## Exposing an external service (TLS passthrough)

For hosts outside the cluster (Proxmox, UniFi, NAS):
1. Create `ExternalName` Service or manual `Endpoints` + `Service`
2. Create `TLSRoute` with `passthrough` mode — TLS terminates at the target, no cert-manager needed
3. See `kubernetes/apps/external/` for existing examples
