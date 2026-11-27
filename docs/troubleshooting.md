# Troubleshooting

Symptom-to-fix tables for the four areas that fail most often. For a Flux
object that is not Ready, start with
[diagnose-kustomization](./runbooks/diagnose-kustomization.md) or
[diagnose-helmrelease](./runbooks/diagnose-helmrelease.md). Why things are set
up this way is in [decisions.md](./decisions.md).

## Storage (Synology NFS CSI)

The Synology CSI runs in namespace `dataplane` and must be healthy before any
PVC workload can schedule. The storage class is always `nfs-csi-storage`
(`nfs-csi-media-storage` for media). The NAS is `192.168.30.99`.

```bash
kubectl get storageclass
kubectl describe pvc <name> -n <namespace>
kubectl logs -n dataplane -l app=synology-csi-node
```

| Symptom | Cause | Fix |
|---------|-------|-----|
| "Couldn't find any host available" | Subfolder bug in older CSI versions | Keep volumes at the share root, not in subfolders |
| PVC stuck `Pending` | NFS export permissions wrong | Add the worker node CIDR to the NFS export allow-list |
| Mount failures | NFS v4.1 unreachable | Check `192.168.30.99` is reachable from the node subnet |
| UID/GID mismatch | Container user differs from NFS permissions | Set `securityContext.fsGroup` to match the export |
| ext4 quota errors | Wrong volume type | Recreate the volume as Btrfs on DSM |

NFS exports must allow the homelab VLAN `192.168.30.0/24`, and the devcontainer
subnet `172.17.0.0/16` when developing locally. Use Btrfs volumes (quota and
shared-folder support) and NFS v4.1 for volumes shared by several pods. To
grow a volume, see [resize-pvc](./runbooks/resize-pvc.md).

## Networking (Cilium and Gateway API)

Use the Kubernetes MCP for resource inspection and fall back to the CLI only for
Cilium connectivity tests it cannot produce.

| Symptom | Check |
|---------|-------|
| Gateway has no IP | `l2announcements.enabled: true` in the Cilium HelmRelease values, and the L2 announcement and IP pool resources |
| TLS fails on a Gateway-terminated route | cert-manager Certificates are Ready (`kubectl get cert -A`) and the wildcard Secret exists |
| Passthrough route fails | `TLSRoute` is attached to the right gateway, DNS points at that gateway's address, and the backend completes a TLS handshake for the SNI |
| Source IP not preserved | Cilium handles this itself; do not set `externalTrafficPolicy` |
| Route does not work | `kubectl get httproute <name> -o yaml` (or `tlsroute`) shows `Accepted` and `Programmed` |

`kubeProxyReplacement` must be `true` for Gateway API to work. Changing the CNI
after deployment is very disruptive; avoid it unless necessary.

To expose an internal service: confirm the Service and port, then add an
`httproute.yaml` attached to Gateway `internal` in namespace `gateway`, section
`https-gateway`, with a host of `<app>.lab.petebeegle.com`. For a host outside
the cluster (Proxmox, UniFi, the NAS) use an `ExternalName` Service, or manual
`Endpoints` plus a Service, and a `TLSRoute` in `passthrough` mode. The
existing examples are in `kubernetes/apps/external/`.

## Observability (Grafana, Loki, Mimir, Alloy)

Alloy collects metrics and logs, Mimir stores metrics, Loki stores logs, and
Grafana shows dashboards and runs alert rules.

| Symptom | Check |
|---------|-------|
| Mimir out of memory | Raise the memory limits in the HelmRelease values; reduce the initial metric burst on restart |
| Loki ingestion errors | Storage backend (MinIO) connectivity and bucket permissions |
| No metrics in Grafana | Alloy is scraping the target (the Service or pod needs `prometheus.io/scrape: "true"`) and the discovery config in `kubernetes/infra/monitoring/alloy/config/config.alloy` is right |
| Alloy not forwarding | The Mimir and Loki endpoint URLs and auth in `config.alloy` |
| Alert fired but no Discord message | Grafana alert state, then the `pretty-discord-alerts` relay: [discord-alert-delivery-health](./runbooks/discord-alert-delivery-health.md) |

## Talos

Talos nodes have no SSH. Use `talosctl` against direct control-plane IPs, never
the Kubernetes API VIP; worker nodes cannot forward Talos API requests. The
kube-apiserver needs a healthy etcd, so check etcd first, then kubelet, then the
controller runtime, then workloads.

```bash
talosctl health --nodes <CP_NODE>
talosctl -n <NODE_IP> etcd members
talosctl -n <NODE_IP> etcd status
talosctl -n <NODE_IP> image ls --namespace system
```

| Symptom | Cause and fix |
|---------|---------------|
| Certificate IP errors | A subnet conflict with the pod CIDR `10.244.0.0/16` or service CIDR `10.96.0.0/12` |
| Talos API unreachable on a worker | Workers cannot forward; target a control-plane IP directly |
| etcd membership looks wrong | Compare the expected control-plane count with `etcd members` |

Upgrades: [upgrade-talos](./runbooks/upgrade-talos.md).

## Flux and Helm

| Symptom | Cause and fix |
|---------|---------------|
| Upgrade fails with `server-side apply failed ... webhooks[n].sideEffects: Required value`, then rolls back | The new chart drops a webhook entry whose CA bundle cert-manager's cainjector injects. Cainjector still owns part of the entry, so server-side apply leaves a stub. Set `spec.upgrade.serverSideApply: disabled` on the HelmRelease (see the intel operator) |
