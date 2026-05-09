# Diagnose Kustomization

Use this runbook when a Flux Kustomization is not Ready, stuck, or blocking downstream resources.

## Dependency Chain

Check upstream dependencies first. A failing upstream Kustomization blocks downstream reconciliation.

```text
crds -> cert-manager/nfs-csi/grafana-operator -> cilium -> certs -> gateway -> monitoring/apps
```

Apps depend on `gateway`; NFS-backed apps also depend on `nfs-csi`.

## Procedure

1. List all Kustomizations.

```bash
kubectl get kustomization -A
```

2. Identify the first unhealthy upstream dependency.

```bash
kubectl get kustomization <name> -n flux-system -o yaml
```

3. Force a reconcile if it is safe to retry.

```bash
flux reconcile kustomization <name> --with-source
```

4. Inspect conditions and events.

```bash
kubectl describe kustomization <name> -n flux-system
```

5. If variable substitution is suspect, inspect computed values.

```bash
flux debug kustomization <name> --show-vars
```

6. Resume if the Kustomization is suspended.

```bash
flux resume kustomization <name>
```

## Common Failures

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| `decryption failed` | `sops-age` missing or wrong | Recreate or correct the Flux SOPS Secret |
| `health check timeout` | Applied resource is not becoming Ready | Check pods, CRDs, PVCs, or route conditions in the target namespace |
| `dependsOn is not ready` | Upstream Kustomization unhealthy | Diagnose the upstream Kustomization first |
| GitRepository source error | Flux cannot fetch the repo | Check GitRepository status and credentials |
| Resource stuck `Terminating` | Finalizer blocking deletion | Inspect the resource and remove finalizer only if safe |

## SOPS Secret Recovery

```bash
kubectl create secret generic sops-age \
  -n flux-system \
  --from-file=age.agekey=~/.config/sops/age/keys.agekey
```

Use the correct environment Age key.
