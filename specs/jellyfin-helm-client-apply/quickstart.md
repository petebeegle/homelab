# Quickstart: Jellyfin Helm Client Apply

```bash
python3 -m unittest tools.development.tests.test_jellyfin_config_migration
python3 tools/architecture/render.py --check
pre-commit run --all-files
```

After merge, verify Helm no longer reports the strategy validation error, the
migration completes, and exact user paths work before considering cleanup.
