# Quickstart: Jellyfin Migration Envsubst Verification

From the implementation worktree:

```bash
python3 -m unittest tools.development.tests.test_jellyfin_config_migration
python3 tools/architecture/render.py --check
pre-commit run --all-files
```

After merge, record the GitHub merge SHA, Flux source fetched SHA, Jellyfin
Kustomization applied SHA, live deployment strategy/PVC/init state, and exact
HTTPS web and SSO-start results in `evidence.md`. Do not remove migration or
rollback assets until every acceptance layer passes.
