---
name: add-app
description: Scaffold a new Kubernetes application in this homelab. Invoke when adding a new app, creating a HelmRelease, or setting up a new namespace with Flux.
---

## Steps

### 1. Create the base config

Create `kubernetes/apps/<app-name>/app.yaml` combining Namespace, HelmRepository (if new), and HelmRelease:

```yaml
---
apiVersion: v1
kind: Namespace
metadata:
  name: <app-name>
  labels:
    name: <app-name>
    pod-security.kubernetes.io/enforce: baseline
    pod-security.kubernetes.io/enforce-version: latest
---
apiVersion: source.toolkit.fluxcd.io/v1
kind: HelmRepository
metadata:
  name: <app-name>
  namespace: flux-system
spec:
  interval: 12h
  url: https://<helm-repo-url>
---
apiVersion: helm.toolkit.fluxcd.io/v2
kind: HelmRelease
metadata:
  name: <app-name>
  namespace: <app-name>
spec:
  interval: 1h
  releaseName: <app-name>
  install:
    crds: CreateReplace
    remediation:
      retries: 3
  upgrade:
    crds: CreateReplace
    remediation:
      retries: 3
      remediateLastFailure: true
  chart:
    spec:
      chart: <chart-name>
      version: "<version>"
      sourceRef:
        kind: HelmRepository
        name: <app-name>
        namespace: flux-system
  values: {}
```

### 2. Create the HTTPRoute

Every app exposed via the cluster needs a Gateway API HTTPRoute (not a traditional Ingress). Create `kubernetes/apps/<app-name>/httproute.yaml`:

```yaml
---
apiVersion: gateway.networking.k8s.io/v1
kind: HTTPRoute
metadata:
  name: <app-name>
  namespace: <app-name>
spec:
  parentRefs:
    - name: internal
      namespace: gateway
      sectionName: https-gateway
  hostnames:
    - <app-name>.lab.petebeegle.com
  rules:
    - matches:
        - path:
            type: PathPrefix
            value: /
      backendRefs:
        - name: <app-name>
          port: <port>
          weight: 1
```

### 3. Create `kustomization.yaml`

```yaml
---
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
resources:
  - app.yaml
  - httproute.yaml
```

If the app has Helm values too complex to inline, use a `values.yaml` with a configMapGenerator:

```yaml
configMapGenerator:
  - name: <app-name>-values
    namespace: <app-name>
    files:
      - values.yaml=values.yaml
configurations:
  - kustomizeconfig.yaml
```

And reference it in the HelmRelease with `valuesFrom` instead of inline `values`.

If the app needs a secret, invoke `add-secret` now before continuing.

### 4. Register in the production overlay

Add the new app to `kubernetes/apps/production/kustomization.yaml`:

```yaml
resources:
  - ../base/<app-name>   # add this line
```

### 5. Verify after committing

After Flux reconciles (or force with `flux reconcile kustomization apps --with-source`):

```bash
kubectl get kustomization -A          # all Ready
kubectl get helmrelease -n <app-name> # Installed
kubectl get pods -n <app-name>        # Running
kubectl get httproute -n <app-name>   # Accepted, Programmed
```
