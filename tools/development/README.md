# Development Tools

`verify_branch_deploy.py` is the canonical live acceptance helper for app-scoped development branch environments. It loads smoke profiles from `tools/development/smoke-profiles/` and currently supports `whoami`, `jellyfin`, and `homepage`.

Operational authority lives in [Development Cluster](../../docs/runbooks/development-cluster.md). Start there for prerequisites, cleanup expectations, and what this tool proves.

```sh
python3 tools/development/verify_branch_deploy.py --app whoami --branch codex/example-change --slug example-change --push
```

The Jellyfin profile verifies the branch namespace, Flux Kustomization and HelmRelease readiness, active pod readiness, config PVC binding on `nfs-csi-storage`, Service existence, HTTPRoute attachment, and an in-cluster HTTP probe against the Jellyfin web shell:

```sh
python3 tools/development/verify_branch_deploy.py --app jellyfin --branch codex/jellyfin-change --slug jellyfin-change --push
```

The Homepage profile verifies the branch namespace, active pod readiness, Service existence, HTTPRoute attachment, and an in-cluster HTTP probe against the dashboard shell:

```sh
python3 tools/development/verify_branch_deploy.py --app homepage --branch codex/homepage-change --slug homepage-change --push
```

Use `--include-cluster-base` to first reconcile the development base from `--branch` in the known order and restore the `flux-system` GitRepository to `main` before the tool exits:

```sh
python3 tools/development/verify_branch_deploy.py --app whoami --branch codex/example-change --slug example-change --push --include-cluster-base
```
