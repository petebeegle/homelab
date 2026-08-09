# Quickstart: Jellyfin Recreate Strategy Verification

```bash
python3 -m unittest tools.development.tests.test_jellyfin_config_migration
helm template jellyfin jellyfin/jellyfin --version 3.2.0 \
  -f kubernetes/apps/jellyfin/values.yaml
python3 tools/architecture/render.py --check
pre-commit run --all-files
```

After merge, record fetched/applied SHAs, Helm conditions, live Deployment
strategy, PVCs, migration init and marker evidence, and exact user paths before
considering a separate cleanup implementation.
