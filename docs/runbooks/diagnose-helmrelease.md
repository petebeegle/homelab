# Diagnose HelmRelease

Use this runbook when a Flux HelmRelease is not Ready, stuck installing or upgrading, or when an app is broken after a chart change.

## Procedure

1. Check HelmRelease status.

```bash
kubectl get helmrelease -A
kubectl get helmrelease <name> -n <namespace> -o yaml
```

Primary signals are in `status.conditions`. Common reasons include `InstallFailed`, `UpgradeFailed`, `DependencyNotReady`, and `ArtifactFailed`.

2. Force a reconcile if it is safe to retry.

```bash
flux reconcile helmrelease <name> -n <namespace> --with-source
```

3. Check chart source when artifacts or versions fail.

```bash
kubectl get helmrepository -A
kubectl describe helmrepository <name> -n flux-system
```

4. Inspect final rendered values when chart values are suspect.

```bash
flux debug helmrelease <name> -n <namespace> --show-values
```

5. Check pods if the HelmRelease is Ready but the app is unhealthy.

```bash
kubectl get pods -n <namespace>
kubectl logs -n <namespace> <pod>
kubectl logs -n <namespace> <pod> --previous
```

## Common Failures

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| `DependencyNotReady` | Upstream Kustomization unhealthy | Diagnose the blocking Kustomization |
| Resource already exists | Failed install left orphaned resources | Delete the orphaned resource if safe, then reconcile |
| Immutable field patch error | Chart changed an immutable selector or field | Delete the affected workload if safe and let Flux recreate it |
| PVC stuck `Pending` | `nfs-csi-storage` missing or NFS unreachable | Check `nfs-csi`, Synology CSI pods, and NAS export permissions |
| Pod `CrashLoopBackOff` | App config/runtime issue | Inspect pod logs and chart values |
| `ArtifactFailed` | HelmRepository cannot fetch index or chart | Verify repository URL, network, and requested chart version |

## Notes

A HelmRelease can report Ready while the workload itself is unhealthy. Treat HelmRelease status as deployment status, then confirm workload health through Kubernetes pods, events, and logs.
