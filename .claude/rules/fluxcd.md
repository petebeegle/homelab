# FluxCD

## Research Resources

1. **Official docs:** https://fluxcd.io/flux/
2. **Troubleshooting:** `flux check`, `flux logs --level=error`
3. **GitHub discussions:** https://github.com/fluxcd/flux2/discussions
4. **Dependency ordering:** https://github.com/fluxcd/flux2/discussions/2276

## Troubleshooting

**Prefer `homelab-mcp` tools** over CLI commands:
- Use `cluster_health` for an aggregated overview (nodes, flux, pods, helmreleases, PVCs)
- Use `flux_status(resource_type="all")` instead of `flux get all -A`
- Use `flux_status(resource_type="kustomization")` instead of `flux get kustomizations`
- Use `flux_status(resource_type="helmrelease", name=<name>, namespace=<ns>)` instead of `flux get helmrelease`
- Use `helmrelease_debug(name=<name>, namespace=<ns>)` instead of `kubectl describe helmrelease`
- Use `flux_reconcile(resource_type=<type>, name=<name>)` instead of `flux reconcile`
- Use `flux_logs(level="error")` instead of `flux logs --level=error`

Fall back to CLI only when MCP tools don't cover the need:
```bash
flux check
flux debug kustomization <name> --show-vars
flux debug helmrelease <name> --show-values
```

**Common issues:**
- "Cannot create empty commit": Already bootstrapped on same branch/path
- HelmRelease stuck: Use `helmrelease_debug` first, then check for CRD ordering issues
- Source not ready: Check GitRepository or HelmRepository status

## Validation Checklist

### Before Applying Kubernetes Changes
- [ ] `pre-commit run --all-files` passes
- [ ] SOPS secrets are encrypted (`sops -d` to verify they decrypt)
- [ ] HelmRelease has correct `dependsOn` if it needs CRDs or storage
- [ ] PVCs reference existing StorageClass (`synology-nfs-storage`)
- [ ] Gateway API routes reference existing Gateway

### After Any Change
- [ ] `cluster_health` shows all kustomizations Ready, no problem pods, no PVC issues
- [ ] `cluster_health` shows all nodes Ready
- [ ] Applications are accessible via Gateway
