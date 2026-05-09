# Upgrade Talos

Use this runbook to upgrade Talos OS or the Kubernetes version managed by Talos.

## Safety Requirements

- Back up etcd before changing Talos or Kubernetes versions.
- Upgrade one node at a time.
- Upgrade control plane nodes before workers.
- Verify health after each node.
- Use direct node IPs, especially direct control plane IPs for cluster checks.

## Back Up Etcd

```bash
talosctl -n <CP_NODE> etcd snapshot /tmp/etcd-$(date +%Y%m%d).snapshot
```

Do not proceed if the snapshot fails.

## Talos OS Upgrade

Pre-checks:

- Check current version with `talosctl version`.
- Review Talos release notes for breaking changes.
- Confirm the target Talos version supports the current Kubernetes version.
- Confirm cluster health.

```bash
talosctl health --nodes <CP_NODE>
```

Upgrade each node:

```bash
talosctl upgrade --nodes <NODE_IP> --image ghcr.io/siderolabs/installer:<version>
```

Verify after each node:

```bash
talosctl health --nodes <CP_NODE>
kubectl get nodes
```

## Kubernetes Upgrade

Pre-checks:

- Confirm the target Kubernetes version is supported by the current Talos version.
- Review Kubernetes release notes for removed or deprecated APIs.
- Confirm Flux and core controllers are healthy before starting.
- Run a dry run first.

```bash
talosctl upgrade-k8s --to <X.Y.Z> --dry-run
```

Apply only after the dry run is clean:

```bash
talosctl upgrade-k8s --to <X.Y.Z>
```

## Post-Upgrade Verification

```bash
kubectl get nodes
kubectl get kustomization -A
kubectl get helmrelease -A
talosctl -n <NODE_IP> logs kubelet
```

Expected outcomes:

- All nodes are Ready and show expected versions.
- Flux Kustomizations continue reconciling.
- HelmReleases do not show new failures.
- Kubelet logs do not show persistent errors.
