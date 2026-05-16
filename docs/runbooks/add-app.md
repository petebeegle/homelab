# Add App

Use this runbook to add a Kubernetes app managed by Flux.

## Inputs

- App name and namespace.
- Deployment style: raw manifests or HelmRelease.
- Exposure model: no route, LAN-only `internal` Gateway route, WireGuard service-plane `external` Gateway route, internet-public Cloudflare `public` Gateway route, or `TLSRoute` passthrough.
- Storage needs, especially whether PVCs require `nfs-csi-storage`.
- Secret needs; if present, also follow `docs/runbooks/add-secret.md`.

## Procedure

1. Create `kubernetes/apps/<app-name>/`.
2. Add `namespace.yaml` or include the Namespace in `app.yaml`.
3. Add the workload manifest or HelmRelease.
4. Add `httproute.yaml` for Gateway-terminated HTTP(S), `httproute-public.yaml` for internet-public Cloudflare HTTP exposure, or `tlsroute.yaml` for TLS passthrough.
5. Add `kustomization.yaml` listing the app resources.
6. Add `kubernetes/clusters/production/apps/<app-name>.yaml` as a Flux Kustomization.
7. Add the new cluster-layer file to `kubernetes/clusters/production/apps/kustomization.yaml`.
8. If the app should be testable in branch environments, add a branch-aware overlay that uses `branch_slug` in names, namespaces, hostnames, and PVC names.
9. Add or select a development smoke profile for the app, or document why the app cannot be smoke-tested in development yet.
10. For routed HTTP apps, add an unauthenticated probe to `tests/smoke/routes.spec.js` or document why the app should be excluded from in-cluster synthetic smoke checks. Prefer durable page-shell text or redirect assertions and add the app Flux Kustomization to `app-synthetics` `dependsOn` when the probe requires the app to exist first.
11. Verify after Flux reconciles.

## Choose Exposure

- Use no route for jobs, private backends, and components reached only through in-cluster Services.
- Use `gateway/internal` for LAN-only Gateway-terminated HTTP(S) on the `192.168.30.x` service plane.
- Use `gateway/external` for WireGuard service-plane Gateway-terminated HTTP(S) on the `192.168.40.x` service plane. This is external to the LAN segment but not internet-public.
- Use `gateway/public` only for internet-public hostnames intentionally opened through Cloudflare Tunnel. Public exposure needs both a cloudflared ingress rule and an app-owned `HTTPRoute`.
- Use `gateway/passthrough` only when a LAN-reachable backend should terminate TLS itself. Use `gateway/external-passthrough` for the same pattern on the WireGuard service plane; it is reserved until a route needs it.

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

Use the internal Gateway for services that should stay on the `192.168.30.x` service plane.

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

## Public Cloudflare HTTPRoute Template

Use the public Gateway only for hostnames intentionally opened through Cloudflare Tunnel. Cloudflared forwards matching public DNS names to `gateway/public` over in-cluster HTTP, and the app owns the `HTTPRoute` that selects the backend Service. This Gateway does not terminate TLS; Cloudflare terminates public HTTPS before forwarding HTTP to the tunnel origin.

```yaml
---
apiVersion: gateway.networking.k8s.io/v1
kind: HTTPRoute
metadata:
  name: <app-name>-public
  namespace: <app-name>
spec:
  parentRefs:
    - name: public
      namespace: gateway
      sectionName: http-gateway
  hostnames:
    - <public-hostname>
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

Add or update the corresponding `ConfigMap/cloudflared` ingress rule so the public hostname targets `http://cilium-gateway-public.gateway.svc.cluster.local:80`, not the app Service directly. Keep the final cloudflared fallback rule as `service: http_status:404`.

## Out-Of-Cluster Service HTTPRoute Template

Use this pattern for a service outside the cluster when the internal Gateway should present the trusted certificate or hide the backend port.
If the backend only accepts HTTPS and cannot present a certificate trusted for the public hostname, add an in-cluster proxy and point the `HTTPRoute` at the proxy. Do not rely on `appProtocol: https` alone to make the Gateway originate HTTPS upstream.

```yaml
---
apiVersion: v1
kind: Service
metadata:
  name: <service-name>
  namespace: external
spec:
  ports:
    - name: http
      protocol: TCP
      port: <backend-port>
      targetPort: <backend-port>
---
apiVersion: discovery.k8s.io/v1
kind: EndpointSlice
metadata:
  name: <service-name>
  namespace: external
  labels:
    kubernetes.io/service-name: <service-name>
addressType: IPv4
ports:
  - name: http
    protocol: TCP
    port: <backend-port>
endpoints:
  - addresses:
      - <backend-ip>
---
apiVersion: gateway.networking.k8s.io/v1
kind: HTTPRoute
metadata:
  name: <service-name>-route
  namespace: external
spec:
  parentRefs:
    - name: internal
      namespace: gateway
      sectionName: <listener-name>
  hostnames:
    - <hostname>
  rules:
    - backendRefs:
        - name: <service-name>
          port: <backend-port>
```

Add a matching Gateway HTTPS listener and cert-manager `Certificate` when the hostname is outside `${cluster_domain}`.

For HTTPS-only external backends with untrusted certificates or backend redirects that expose ports, use a small proxy Deployment instead of routing directly to the external `EndpointSlice`. The proxy can connect to the backend over HTTPS, set forwarded headers, and normalize redirects or response bodies before returning traffic to the Gateway route.

## WireGuard External HTTPRoute Template

Use this pattern for services that should be reachable on the `192.168.40.x` service plane through WireGuard. This `external` Gateway is VPN/service-plane exposure, not internet-public exposure.

```yaml
---
apiVersion: gateway.networking.k8s.io/v1
kind: HTTPRoute
metadata:
  name: <app-name>
  namespace: <app-name>
spec:
  parentRefs:
    - name: external
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

## LAN TLSRoute Passthrough Template

Use this pattern only when the external service should terminate TLS itself and already presents an acceptable certificate for the hostname on the internal `192.168.30.x` passthrough Gateway.
Define the backing `Service` and `EndpointSlice` with the target TLS port, as shown in the out-of-cluster HTTPRoute example. Also confirm the `TLSRoute` file is listed in the app Kustomization, DNS outside this repo points the hostname at the passthrough Gateway when applicable, and the backend accepts the expected SNI.

```yaml
---
apiVersion: gateway.networking.k8s.io/v1alpha2
kind: TLSRoute
metadata:
  name: <service-name>-route
  namespace: external
spec:
  parentRefs:
    - name: passthrough
      namespace: gateway
  hostnames:
    - <hostname>
  rules:
    - backendRefs:
        - name: <service-name>
          port: <tls-port>
```

## WireGuard TLSRoute Passthrough Template

Use this pattern for TLS passthrough services that should be reachable on the `192.168.40.x` service plane through WireGuard. `gateway/external-passthrough` is reserved for this pattern; validate route attachment, DNS, and backend SNI before treating a new route as ready.

```yaml
---
apiVersion: gateway.networking.k8s.io/v1alpha2
kind: TLSRoute
metadata:
  name: <service-name>-route
  namespace: external
spec:
  parentRefs:
    - name: external-passthrough
      namespace: gateway
      sectionName: tls-passthrough
  hostnames:
    - <hostname>
  rules:
    - backendRefs:
        - name: <service-name>
          port: <tls-port>
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

List `httproute-public.yaml` or `tlsroute.yaml` here when the app uses those exposure files.

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

## Branch-Aware App Overlay

Use `branch_slug`, not slot terminology. Branch app hostnames must follow `<app>-${branch_slug}.development.lab.petebeegle.com`, and branch resources must be unique enough to coexist with the development base and other branch apps.

For raw manifests, create an overlay such as `kubernetes/apps/<app-name>/branch/` with:

- Namespace: `<app-name>-${branch_slug}`
- Workload and Service names: `<app-name>-${branch_slug}`
- HTTPRoute hostname: `<app-name>-${branch_slug}.${cluster_domain}`
- PVC names, if any: `<app-name>-${branch_slug}-<purpose>`
- A branch-specific `ReferenceGrant` in `gateway` when the route references a shared Gateway from a branch namespace

Cluster-layer branch activations should live under a reviewed development path, point their `sourceRef` at a branch-specific `GitRepository`, set `postBuild.substitute.branch_slug`, and remain `suspend: true` until the referenced branch exists. See `kubernetes/clusters/development/branches/` and `kubernetes/apps/whoami/branch/` for the initial template.

Cluster-scoped changes, including CRDs, controllers, Gateway API shared objects, and storage classes, are tested sequentially on the development base. Do not fan those changes out through parallel branch environments.

## Development Testing

New production apps are not considered complete until development testing is addressed. Prefer adding or selecting a config-driven smoke profile as described in `docs/runbooks/development-cluster.md`. If the app cannot be tested in development yet, record a documented exception in the implementation plan and PR summary with the missing dependency and follow-up needed.

For each new app, validate the applicable items before production activation is considered complete:

- Workload readiness: Deployments, StatefulSets, DaemonSets, or HelmRelease-managed pods become Ready in the development branch namespace.
- Routes: `HTTPRoute` or `TLSRoute` attaches to the intended Gateway and reports healthy conditions expected for that route type.
- Storage: PVCs use `nfs-csi-storage` unless intentionally exempted, bind successfully, mount into the workload, and clean up with the branch namespace unless retained for debugging.
- Secrets: Secret references render with the expected names, required development secret/config files are staged when needed, and secret contents are never logged.
- Branch overlay: Namespaces, workload names, hostnames, PVC names, and route references use `branch_slug` and can coexist with the development base.
- App-specific probes: Exercise a meaningful health endpoint, login-free HTTP path, protocol handshake, or command that proves the app is serving more than a scheduled pod.

When `tools/development/verify_branch_deploy.py` supports the selected profile, run it against the exact branch `HEAD` that will be reviewed. Until profile expansion supports the app, record manual smoke commands and observations instead of changing harness behavior inside the app PR.

## Verification

```bash
kubectl get kustomization -A
kubectl get helmrelease -n <app-name>
kubectl get pods -n <app-name>
kubectl get gateway -n gateway
kubectl get httproute -n <app-name>
kubectl get tlsroute -n <app-name>
```

Expected route conditions are `Accepted=True` and `Programmed=True`. For public apps, also verify the matching cloudflared ingress rule targets `http://cilium-gateway-public.gateway.svc.cluster.local:80`. For passthrough routes, verify the route attaches to the selected Gateway and the backend TLS handshake works with the route hostname as SNI.
