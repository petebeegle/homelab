# Homepage

Homepage serves the LAN and WireGuard dashboard at `https://${cluster_domain}`. It is not exposed through the public Cloudflare Gateway.

## Configuration

Public, non-sensitive configuration lives in `ConfigMap/homepage-public-config` in this directory. The app also mounts an optional `ConfigMap/homepage-private-config` from `homelab-private`; the private ConfigMap may be absent and startup must still succeed.

Homepage reads merged files from `/app/config`. Public and private files are mounted read-only under separate directories, then an initContainer builds `/app/config` before the app starts. A sidecar re-runs the same merge periodically while the app is running.

Merge contract:

- `services.yaml`, `bookmarks.yaml`, and `widgets.yaml`: append public entries, then private entries.
- `settings.yaml`, `kubernetes.yaml`, and `docker.yaml`: recursively merge maps, with private values overriding public values.
- `custom.css` and `custom.js`: concatenate public content, then private content.
- Missing private files are treated as empty.

Private config should use the same namespace and filenames:

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: homepage-private-config
  namespace: homepage
data:
  services.yaml: |
    []
```

## DNS

The root `${cluster_domain}` hostname must resolve to the Cilium Gateway service plane being used by the client. LAN DNS should point it at `gateway/internal`; WireGuard DNS points both the root name and wildcard names at `gateway/external`.
