# Networking: Cilium & Gateway API

## Research Resources

1. **Cilium docs:** https://docs.cilium.io/en/stable/
2. **Gateway API support:** https://docs.cilium.io/en/stable/network/servicemesh/gateway-api/gateway-api/
3. **Key setting:** `kubeProxyReplacement: true` required for Gateway API

## Troubleshooting

```bash
# Check Cilium status
cilium status

# Check Gateway resources
kubectl get gateways -A
kubectl get httproutes -A
kubectl get tlsroutes -A

# Check Cilium logs
kubectl logs -n kube-system -l k8s-app=cilium

# Verify connectivity
cilium connectivity test
```

**Common issues:**
- Gateway not getting IP: Check `l2announcements.enabled: true` in Cilium config
- TLS not working: Verify cert-manager certificates are Ready
- Source IP not preserved: Cilium handles this automatically, no `externalTrafficPolicy` needed
- Changing CNI after deployment causes major disruption - avoid if possible

## Patterns

### Exposing a Service via Gateway API

1. Ensure service exists and has correct port
2. Create HTTPRoute or TLSRoute referencing the Gateway in `kubernetes/infra/network/`
3. For TLS, create Certificate resource referencing cert-manager ClusterIssuer
4. Verify: `kubectl get httproute <name> -o yaml` shows attached to Gateway

### Adding External Service Access

For services outside the cluster (like Proxmox, UniFi):
1. Create ExternalName Service or Endpoints + Service
2. Create TLSRoute with `passthrough` for TLS passthrough
3. See `kubernetes/apps/base/external/` for examples
