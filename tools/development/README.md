# Development Tools

`verify_branch_deploy.py` is the canonical live acceptance helper for app-scoped development branch environments. It loads JSON smoke profiles from `tools/development/smoke-profiles/`.

Supported profiles:

- `whoami`: verifies the branch namespace, active pod readiness, Service, and HTTPRoute.
- `synthetics`: verifies the suspended branch CronJob, smoke source ConfigMap, development domain substitution, and a temporary Playwright JavaScript discovery Job.

Operational authority lives in [Development Cluster](../../docs/runbooks/development-cluster.md). Start there for prerequisites, cleanup expectations, and what this tool proves.

```sh
python3 tools/development/verify_branch_deploy.py --app whoami --branch codex/example-change --slug example-change --push
```

Verify the synthetic smoke deployment path without running route probes:

```sh
python3 tools/development/verify_branch_deploy.py --app synthetics --branch codex/example-change --slug example-change --push
```

Use `--include-cluster-base` to first reconcile the development base from `--branch` in the known order and restore the `flux-system` GitRepository to `main` before the tool exits:

```sh
python3 tools/development/verify_branch_deploy.py --app whoami --branch codex/example-change --slug example-change --push --include-cluster-base
```
