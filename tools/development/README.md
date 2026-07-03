# Development Tools

`verify_branch_deploy.py` is the canonical live acceptance helper for app-scoped development branch environments. It loads smoke profiles from `tools/development/smoke-profiles/` and currently supports `whoami`, `jellyfin`, and `home-assistant`.

Operational authority lives in [Development Cluster](../../docs/runbooks/development-cluster.md). Start there for prerequisites, cleanup expectations, and what this tool proves.

Before running live smoke from an implementation or verifier clone, stage the
development Terraform vars from the main checkout into the clone that will run
the command:

```sh
.codex/scripts/prepare_development_smoke_secrets.sh example-change /workspaces/homelab-ideas/example-change
```

```sh
python3 tools/development/verify_branch_deploy.py --app whoami --branch codex/example-change --slug example-change --push
```

The profile schema supports:

- `checks.kustomizations`: Flux `Kustomization` names in `flux-system` that must be Ready.
- `checks.helmReleases`: HelmRelease names in the profile namespace that must be Ready.
- `checks.services`: Service names that must exist.
- `checks.httpRoutes` and `checks.tlsRoutes`: Gateway API routes that must have `Accepted` and `ResolvedRefs` on one parent.
- `checks.secretRefs`: Kubernetes Secret names that must exist in the profile namespace. The verifier checks names only and does not request or print Secret data.
- `checks.pvcs`: PVC names and optional `storageClass` expectations.
- `checks.httpProbes`: in-cluster curl probes against Services.
- `routeUrls`: rendered external route URLs for browser or Playwright handoff.

Print route URLs without touching the cluster:

```sh
python3 tools/development/verify_branch_deploy.py --app whoami --branch codex/example-change --slug example-change --print-route-urls
```

The Jellyfin profile verifies the branch namespace, Flux Kustomization and HelmRelease readiness, active pod readiness, config PVC binding on `nfs-csi-storage`, Service existence, HTTPRoute attachment, and an in-cluster HTTP probe against the Jellyfin web shell:

```sh
python3 tools/development/verify_branch_deploy.py --app jellyfin --branch codex/jellyfin-change --slug jellyfin-change --push
```

The Home Assistant profile verifies the branch namespace, Flux Kustomization readiness, active pod readiness, config PVC binding on `nfs-csi-storage`, Service existence, HTTPRoute attachment, and an in-cluster HTTP probe against the Home Assistant web shell:

```sh
python3 tools/development/verify_branch_deploy.py --app home-assistant --branch codex/ha-change --slug ha-change --push
```

Use `--include-cluster-base` to first reconcile the development base from `--branch` in the known order and restore the `flux-system` GitRepository to `main` before the tool exits:

```sh
python3 tools/development/verify_branch_deploy.py --app whoami --branch codex/example-change --slug example-change --push --include-cluster-base
```
