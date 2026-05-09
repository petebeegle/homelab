# Add App

Use this runbook to add a Kubernetes app managed by Flux.

## Inputs

- App name and namespace.
- Deployment style: raw manifests or HelmRelease.
- Exposure model: no route, internal `HTTPRoute`, or external `TLSRoute`.
- Storage needs, especially whether PVCs require `nfs-csi-storage`.
- Secret needs; if present, also follow `docs/runbooks/add-secret.md`.

## Procedure

1. Create `kubernetes/apps/<app-name>/`.
2. Add `namespace.yaml` or include the Namespace in `app.yaml`.
3. Add the workload manifest or HelmRelease.
4. Add `httproute.yaml` if the app is exposed internally.
5. Add `kustomization.yaml` listing the app resources.
6. Add `kubernetes/clusters/production/apps/<app-name>.yaml` as a Flux Kustomization.
7. Add the new cluster-layer file to `kubernetes/clusters/production/apps/kustomization.yaml`.
8. Verify after Flux reconciles.

## HelmRelease Template

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
  interval: 5m
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

## Internal HTTPRoute Template

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
    - <app-name>.${cluster_domain}
  rules:
    - matches:
        - path:
            type: PathPrefix
            value: /
      backendRefs:
        - name: <service-name>
          port: <port>
          weight: 1
```

## App Kustomization Template

```yaml
---
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
resources:
  - namespace.yaml
  - app.yaml
  - httproute.yaml
```

For large Helm values, create `values.yaml`, generate a ConfigMap, and reference it with `valuesFrom`.

## Cluster Flux Kustomization Template

```yaml
---
apiVersion: kustomize.toolkit.fluxcd.io/v1
kind: Kustomization
metadata:
  name: app-<app-name>
  namespace: flux-system
spec:
  interval: 5m
  retryInterval: 2m
  path: ./kubernetes/apps/<app-name>
  prune: true
  wait: true
  sourceRef:
    kind: GitRepository
    name: flux-system
  dependsOn:
    - name: gateway
  postBuild:
    substituteFrom:
      - kind: ConfigMap
        name: cluster-vars
```

Add `- name: nfs-csi` under `dependsOn` when the app uses NFS-backed PVCs.

## Verification

```bash
kubectl get kustomization -A
kubectl get helmrelease -n <app-name>
kubectl get pods -n <app-name>
kubectl get httproute -n <app-name>
```

Expected route conditions are `Accepted=True` and `Programmed=True`.
