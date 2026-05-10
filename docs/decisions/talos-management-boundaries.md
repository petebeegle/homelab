---
id: ADR-0006
status: accepted
scope:
  - talos
  - operations
  - nodes
authority: binding
created: 2026-05-09
last_verified: 2026-05-10
supersedes: []
superseded_by:
---

# Talos Management Boundaries

## Decision

Manage Talos nodes only through the Talos API with `talosctl`. Do not use SSH-based node administration.

## Rationale

- Talos is intentionally API-managed and immutable.
- Direct control plane endpoints are more reliable for management than VIPs.
- Worker nodes cannot forward Talos API requests.

## Consequences

- Target direct control plane IPs for cluster-level Talos operations.
- Do not target the Kubernetes API VIP as a Talos API endpoint.
- Use diagnostic order: etcd, kubelet, controller runtime, then Kubernetes workloads.

## Operational Notes

```bash
talosctl health --nodes <CP_NODE>
talosctl -n <NODE_IP> etcd members
talosctl -n <NODE_IP> etcd status
talosctl -n <NODE_IP> image ls --namespace system
```

Common checks:

- Certificate IP errors can come from subnet conflicts with pod CIDR `10.244.0.0/16` or service CIDR `10.96.0.0/12`.
- If an API call fails against a worker, retry against a direct control plane node IP.
- If etcd membership looks wrong, compare expected control plane nodes with `etcd members`.
