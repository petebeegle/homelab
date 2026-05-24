---
status: current
scope:
  - production-stability
  - kubernetes
  - monitoring
  - identity
created: 2026-05-24
last_verified: 2026-05-24
---

# Stabilize Overloaded Services

Use this runbook when many unrelated services show probe timeouts, slow API responses, database timeouts, or write/query latency at the same time. In this homelab, cross-service probe failures are usually a node pressure signal until proven otherwise.

## Triage

1. Check node pressure and pod placement before restarting applications.

   ```bash
   kubectl top nodes
   kubectl get pods -A -o wide --sort-by=.spec.nodeName
   kubectl describe node <node>
   ```

2. Look for critical pods running as `BestEffort` or with CPU requests far below observed usage.

   ```bash
   kubectl get pods -A -o custom-columns='NAMESPACE:.metadata.namespace,NAME:.metadata.name,NODE:.spec.nodeName,QOS:.status.qosClass'
   ```

3. Treat liveness probe failures during broad CPU pressure as symptoms. Prefer adding durable resource requests, limits, and conservative probe thresholds in Git before making repeated live restarts.

4. For multi-replica services such as Cloudflared or query paths, check whether replicas are colocated on the same overloaded node. Add topology spread or anti-affinity in Git when placement contributes to the outage.

## Grafana Operator Duplicate Reconciliation

Grafana API contention can come from two Grafana operators reconciling the same Grafana custom resources. The CRD-only install path must render only Grafana operator CRDs. A HelmRelease that uses the `grafana/grafana-operator` chart with `operator.enabled=false` is not sufficient for chart `5.23.0`; that chart still renders an operator Deployment.

Check for duplicate operators:

```bash
kubectl get deploy -A | grep grafana-operator
kubectl get pods -A -l app.kubernetes.io/name=grafana-operator -o wide
```

The durable fix is to keep exactly one Grafana operator controller and install Grafana operator CRDs from an upstream CRD-only Kustomize source. If a duplicate operator was live, remove it through GitOps and then confirm only the intended `grafana-operator` namespace deployment remains.

## Authentik And PostgreSQL

When Authentik server and worker pods flap together, check PostgreSQL first. NFS-backed PostgreSQL can surface slow checkpoints as server and worker readiness failures.

```bash
kubectl -n authentik logs statefulset/authentik-postgresql --tail=200
kubectl -n authentik get pods -o wide
kubectl -n authentik describe pod -l app.kubernetes.io/component=server
```

Prefer durable tuning in the Authentik Helm values: PostgreSQL CPU and memory requests, checkpoint settings that spread writes over time, and less brittle Authentik server and worker probe timeouts.

## Recovery Notes

- Keep production live changes temporary unless a specific incident runbook says otherwise.
- Record any emergency live changes and make the intended state durable in this repository before considering the incident closed.
- After Flux reconciles a stabilization change, confirm affected Kustomizations and HelmReleases are Ready and watch node CPU, pod restarts, Grafana API latency, Loki writes, Mimir queries, Authentik login, Pi-hole DNS, and Cloudflared tunnel readiness.
