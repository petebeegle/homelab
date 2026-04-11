# Talos OS — node management

## Critical constraints

- **No SSH on Talos nodes** — all management via `talosctl` API
- **Never use VIP as Talos API endpoint** — use direct control plane IPs
- **Worker nodes cannot forward API requests** — always target control plane IPs
- **Diagnostic order:** kube-apiserver requires healthy etcd → check etcd → kubelet → controller-runtime

## Key commands

```bash
talosctl health --nodes <CP_NODE>
talosctl -n <NODE_IP> etcd members
talosctl -n <NODE_IP> etcd status
talosctl -n <NODE_IP> image ls --namespace system
```

## Common issues

- **Certificate IP errors:** Check for subnet conflicts with `10.244.0.0/16` (pods) or `10.96.0.0/12` (services)
- **API unreachable on worker:** Workers can't forward — target CP node IP directly
- **etcd member mismatch:** Run `etcd members` to verify expected count matches live nodes
