---
name: diagnose-helmrelease
description: Diagnose a Flux HelmRelease that is not Ready, stuck upgrading, or failing to install. Invoke when a HelmRelease shows False/Unknown status or an app isn't running after a chart change.
---

## Procedure

### Step 1 — Get current status

Use the `kubernetes` MCP to check all HelmReleases or a specific one:

```bash
kubectl get helmrelease -A
kubectl get helmrelease <name> -n <namespace> -o yaml
```

The `Status.Conditions` block is the primary signal. Common condition reasons: `InstallFailed`, `UpgradeFailed`, `DependencyNotReady`, `ArtifactFailed`.

### Step 2 — Force reconcile

```bash
flux reconcile helmrelease <name> -n <namespace> --with-source
```

The error surfaced here is usually more specific than the cached status message.

### Step 3 — Check the chart source

If the condition shows `ArtifactFailed` or the chart version can't be found:

```bash
kubectl get helmrepository -A
kubectl describe helmrepository <name> -n flux-system
```

Verify the repository URL is reachable and the chart version exists in the index.

### Step 4 — Inspect rendered values

If the release is failing on install/upgrade with a values error:

```bash
flux debug helmrelease <name> -n <namespace> --show-values
```

Confirm the final merged values look correct, especially secrets referenced via `valuesFrom`.

### Step 5 — Trace the specific failure

| Symptom | Cause | Fix |
|---|---|---|
| `DependencyNotReady` | Upstream kustomization unhealthy | Run `diagnose-kustomization` on the blocking kustomization |
| `InstallFailed: rendered manifests contain a resource that already exists` | Prior failed install left orphaned resources | Delete the orphaned resource manually, then reconcile |
| `UpgradeFailed: cannot patch ... field is immutable` | Immutable field changed (e.g. label selector) | Delete the Deployment/StatefulSet and let Flux recreate it |
| PVC stuck `Pending` | StorageClass `nfs-csi-storage` not available or NFS unreachable | Check `controllers` kustomization — Synology CSI must be healthy first |
| Pod in `CrashLoopBackOff` after successful install | App misconfiguration, not a Flux issue | Check pod logs directly: `kubectl logs -n <namespace> <pod>` |
| `ArtifactFailed` | HelmRepository can't fetch index | Check network, verify repo URL in HelmRepository spec |

### Step 6 — Check pod logs if the release succeeded but the app is broken

A HelmRelease can show `Ready=True` while the app itself is crashing. Check:

```bash
kubectl get pods -n <namespace>
kubectl logs -n <namespace> <pod> --previous   # if crash-looping
```
