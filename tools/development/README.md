# Development Tools

`verify_branch_deploy.py` is the canonical live acceptance helper for app-scoped development branch environments. V1 supports `whoami` only. It verifies the branch namespace, active pod readiness, the whoami Service, and the HTTPRoute.

Operational authority lives in [Development Cluster](../../docs/runbooks/development-cluster.md). Start there for prerequisites, cleanup expectations, and what this tool proves.

```sh
python3 tools/development/verify_branch_deploy.py --app whoami --branch codex/example-change --slug example-change --push
```

Use `--include-cluster-base` to first reconcile the development base from `--branch` in the known order and restore the `flux-system` GitRepository to `main` before the tool exits:

```sh
python3 tools/development/verify_branch_deploy.py --app whoami --branch codex/example-change --slug example-change --push --include-cluster-base
```
