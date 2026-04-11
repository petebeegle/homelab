---
name: upgrade-talos
description: Upgrade Talos OS or Kubernetes version on this homelab cluster. Invoke when bumping Talos or Kubernetes versions, or when Renovate opens a PR for either.
---

## Before starting — back up etcd

```bash
talosctl -n <CP_NODE> etcd snapshot /tmp/etcd-$(date +%Y%m%d).snapshot
```

Do not proceed if this fails.

## Upgrading Talos OS

### Pre-upgrade checklist
- [ ] Check current version: `talosctl version`
- [ ] Review Talos release notes for breaking changes
- [ ] Verify target version supports current Kubernetes version
- [ ] Confirm cluster is fully healthy: `talosctl health --nodes <CP_NODE>`

### Procedure
Upgrade one node at a time. Control plane nodes first, then workers.

```bash
# Upgrade a single node
talosctl upgrade --nodes <NODE_IP> --image ghcr.io/siderolabs/installer:<version>

# After each node — verify cluster health before continuing
talosctl health --nodes <CP_NODE>
kubectl get nodes   # all Ready
```

## Upgrading Kubernetes

### Pre-upgrade checklist
- [ ] Target Kubernetes version is supported by current Talos version (check Talos support matrix)
- [ ] Scan manifests for deprecated APIs: `kubectl api-resources` and check release notes
- [ ] Review Kubernetes release notes for breaking changes
- [ ] Dry-run first (catches incompatibilities without applying)

### Procedure

```bash
# Dry run — fix any issues before applying
talosctl upgrade-k8s --to <X.Y.Z> --dry-run

# Apply when dry-run is clean
talosctl upgrade-k8s --to <X.Y.Z>
```

### Post-upgrade verification

```bash
kubectl get nodes                    # all Ready, correct version
kubectl get kustomization -A         # all kustomizations still reconciling
kubectl get helmrelease -A           # no HelmReleases failed
talosctl -n <NODE_IP> logs kubelet   # no errors
```
