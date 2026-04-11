---
name: diagnose-kustomization
description: Diagnose a Flux Kustomization that is not Ready, stuck, or failing to reconcile. Invoke when a kustomization shows False/Unknown status or is blocking downstream resources.
---

## Dependency chain — check this first

Kustomizations have hard `dependsOn` relationships. A failure upstream silently blocks everything downstream:

```
crds → controllers → network → monitoring → apps
```

If `apps` is stuck, always check `controllers` and `network` first before diving into `apps` itself.

## Procedure

### Step 1 — Get current status across all kustomizations

Use the `kubernetes` MCP to list all kustomizations and identify which are not Ready:

```bash
kubectl get kustomization -A
```

Note which kustomization is unhealthy and whether any of its `dependsOn` entries are also unhealthy.

### Step 2 — Force reconcile and observe

```bash
flux reconcile kustomization <name> --with-source
```

Watch what error surfaces immediately after — this is usually more informative than the cached status message.

### Step 3 — Inspect conditions and events

Use the `kubernetes` MCP to get the full resource:

```bash
kubectl describe kustomization <name> -n flux-system
```

Look at:
- `Status.Conditions` — the `Ready` condition message is usually the root cause
- `Status.LastHandledReconcileAt` — if stale, reconciliation isn't running
- Events — SOPS errors, health check timeouts, prune failures surface here

### Step 4 — Trace the specific failure

| Symptom | Cause | Fix |
|---|---|---|
| `decryption failed` | `sops-age` secret missing from cluster | Recreate it: `kubectl create secret generic sops-age -n flux-system --from-file=age.agekey=~/.config/sops/age/keys.agekey` |
| `health check timeout` | A resource in the kustomization isn't becoming Ready | Check pods in that namespace — likely a dep on storage or CRDs |
| `dependsOn is not ready` | Upstream kustomization is unhealthy | Go up the chain and diagnose that one first |
| `unable to get 'flux-system/flux-system'` | GitRepository source error | Check GitRepository status and credentials |
| Resource stuck in `Terminating` | Finalizer blocking deletion | Check the resource directly and remove the finalizer if safe |

### Step 5 — If suspended

```bash
flux resume kustomization <name>
```

Kustomizations can get suspended during manual intervention and left that way.
