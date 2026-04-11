---
name: talos
description: Talos Linux reference for this homelab. Invoke when troubleshooting node issues, upgrading Talos OS or Kubernetes, dealing with etcd, kubelet, or certificate errors, or any time talosctl is involved. Remember: no SSH on Talos nodes, all management is via talosctl API.
---

## Troubleshooting

Use `talosctl` for node management and logs (Talos operations are not covered by the Kubernetes MCP):
```bash
# Overall cluster health check
talosctl health --nodes <CP_NODE>

# etcd health (control plane only)
talosctl -n <NODE_IP> etcd members
talosctl -n <NODE_IP> etcd status

# Service logs (e.g. kubelet, etcd, apid)
talosctl -n <NODE_IP> logs kubelet
talosctl -n <NODE_IP> logs etcd

# Kernel logs
talosctl -n <NODE_IP> dmesg

# Runtime events stream
talosctl -n <NODE_IP> events

# Running processes
talosctl -n <NODE_IP> processes

# Inspect Talos resources (e.g. NetworkInterfaces, StaticPods)
talosctl -n <NODE_IP> get <resource-type>

# Verify images are available
talosctl -n <NODE_IP> image ls --namespace system
```

**Troubleshooting order:** Always start with kube-apiserver, which requires healthy etcd. Check etcd → kubelet → controller-runtime.

**Common issues:**
- Certificate IP errors: Check for subnet conflicts with 10.244.0.0/16 (pods) or 10.96.0.0/12 (services)
- Never use VIP as Talos API endpoint
- Worker nodes cannot forward API requests - always use control plane IPs

## Research Resources

1. **Official docs:** https://www.talos.dev/latest/
2. **Troubleshooting:** https://www.talos.dev/v1.10/introduction/troubleshooting/
3. **GitHub issues:** https://github.com/siderolabs/talos/issues
4. **Key constraint:** No SSH - all management via `talosctl` API

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
