# Contract: Jellyfin Helm Action Mode

The rendered `HelmRelease/jellyfin` must contain:

```yaml
spec:
  upgrade:
    serverSideApply: disabled
  rollback:
    serverSideApply: disabled
```

Neither action may set `force: true`. Existing remediation, chart, values,
post-renderer, and migration behavior remain present.
