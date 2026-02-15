# Talos Linux

## Research Resources

1. **Official docs:** https://www.talos.dev/latest/
2. **Troubleshooting:** https://www.talos.dev/v1.10/introduction/troubleshooting/
3. **GitHub issues:** https://github.com/siderolabs/talos/issues
4. **Key constraint:** No SSH - all management via `talosctl` API

## Troubleshooting

**Prefer `homelab-mcp` tools** over CLI commands:
- Use `talos_nodes()` for all node status and service health (auto-discovers IPs)
- Use `talos_nodes(node=<name-or-ip>)` for a specific node
- Use `talos_logs(node=<ip>, service="kubelet")` instead of `talosctl logs kubelet`
- Use `talos_logs(node=<ip>, service="etcd")` for etcd logs
- Use `talos_logs(node=<ip>, service="controller-runtime")` for controller-runtime logs

Fall back to `talosctl` only when MCP tools don't cover the need:
```bash
# Check etcd health (control plane only)
talosctl -n <NODE_IP> etcd members

# Verify images are available
talosctl -n <NODE_IP> image ls --namespace system
```

**Troubleshooting order:** Always start with kube-apiserver, which requires healthy etcd. Check etcd → kubelet → controller-runtime.

**Common issues:**
- Certificate IP errors: Check for subnet conflicts with 10.244.0.0/16 (pods) or 10.96.0.0/12 (services)
- Never use VIP as Talos API endpoint
- Worker nodes cannot forward API requests - always use control plane IPs

## Upgrade Checklists

### Before Upgrading Talos
- [ ] Backup etcd: `talosctl -n <CP_NODE> etcd snapshot /tmp/etcd.snapshot`
- [ ] Check current version: `talosctl version`
- [ ] Review Talos release notes for breaking changes
- [ ] Upgrade one node at a time, verify cluster health between nodes

### Before Upgrading Kubernetes
- [ ] Talos version supports target K8s version
- [ ] Check deprecated APIs in current manifests
- [ ] Review K8s release notes for breaking changes
- [ ] Use `--dry-run` first: `talosctl upgrade-k8s --to X.Y.Z --dry-run`
