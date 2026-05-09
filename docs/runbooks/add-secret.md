# Add Secret

Use this runbook to add a SOPS-encrypted Kubernetes Secret.

## Critical Constraint

The secret file must be named `secret.yaml` unless `.sops.yaml` is updated. Current encryption rules match:

- `secret.yaml`
- `grafana-env.yaml`

Do not stage plaintext secrets.

## Procedure

1. Create `kubernetes/apps/<app-name>/secret.yaml`.
2. Encrypt the file immediately.
3. Verify decryption before staging.
4. Add `secret.yaml` to the app `kustomization.yaml`.
5. Reference the Secret from the workload or HelmRelease.
6. Verify Flux can decrypt and apply it.

## Secret Template

```yaml
---
apiVersion: v1
kind: Secret
metadata:
  name: <app-name>-<purpose>
  namespace: <app-name>
type: Opaque
stringData:
  key: value
```

## Encrypt And Verify

```bash
sops -i -e kubernetes/apps/<app-name>/secret.yaml
sops -d kubernetes/apps/<app-name>/secret.yaml
```

If `sops -d` fails or the file remains plaintext, stop and fix encryption before `git add`.

## Add To Kustomization

```yaml
resources:
  - app.yaml
  - secret.yaml
  - httproute.yaml
```

## HelmRelease References

Use the chart's supported mechanism. Common patterns:

```yaml
values:
  existingSecret: <app-name>-<purpose>
```

or environment injection:

```yaml
values:
  envFrom:
    - secretRef:
        name: <app-name>-<purpose>
```

## Flux Decryption

Flux uses SOPS decryption through the `sops-age` Secret in `flux-system`. If reconciliation fails with a SOPS error, verify that Secret exists and contains the environment Age key.
