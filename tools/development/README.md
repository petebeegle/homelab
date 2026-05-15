# Development Tools

`verify_branch_deploy.py` is the canonical live acceptance helper for app-scoped development branch environments. V1 supports `whoami` only.

Operational authority lives in [Development Cluster](../../docs/runbooks/development-cluster.md). Start there for prerequisites, cleanup expectations, and what this tool proves.

```sh
python3 tools/development/verify_branch_deploy.py --app whoami --branch codex/example-change --slug example-change --push
```
