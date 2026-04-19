---
name: add-secret
description: Create a SOPS-encrypted Kubernetes secret in this homelab. Invoke when adding credentials, API keys, or any sensitive values to an application.
---

## Critical constraint: filename must be `secret.yaml`

SOPS only encrypts files matching the path patterns in `.sops.yaml`:
- `secret.yaml`
- `grafana-env.yaml`

**Any other filename will not be encrypted.** If you need a descriptive name, use `secret.yaml` — context comes from the namespace and Secret `name` field.

## Steps

### 1. Create `secret.yaml` in the app's base directory

Place it alongside `app.yaml` in `kubernetes/apps/<app-name>/secret.yaml`. The namespace must match the app's namespace:

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: <app-name>-<purpose>
  namespace: <app-name>
type: Opaque
stringData:
  key: value
```

### 2. Encrypt in-place before doing anything else

```bash
sops -i -e kubernetes/apps/<app-name>/secret.yaml
```

### 3. Verify it encrypted correctly — before `git add`

```bash
sops -d kubernetes/apps/<app-name>/secret.yaml
```

If it decrypts and shows your values, it was encrypted correctly. If `sops -d` fails or shows raw values, do not proceed.

### 4. Add to `kustomization.yaml`

```yaml
resources:
  - app.yaml
  - secret.yaml
  - httproute.yaml
```

### 5. Reference in the HelmRelease

Reference the secret by name in the HelmRelease `values:` block (exact keys depend on the Helm chart):

```yaml
values:
  existingSecret: <app-name>-<purpose>
```

Or mount it as an environment variable via `envFrom` / `extraEnvFrom` depending on the chart.

## How Flux decrypts it

The top-level `apps` Kustomization (`kubernetes/clusters/production/apps.yaml`) has:

```yaml
decryption:
  provider: sops
  secretRef:
    name: sops-age
```

Flux handles decryption automatically — no extra config needed per app.
