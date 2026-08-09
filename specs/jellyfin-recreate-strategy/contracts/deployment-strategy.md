# Contract: Jellyfin Deployment Strategy

For Jellyfin chart version `3.2.0` rendered with
`kubernetes/apps/jellyfin/values.yaml`:

1. The Deployment strategy mapping contains `type: Recreate`.
2. The same mapping contains `rollingUpdate: null` so server-side apply clears
   the field inherited from the live RollingUpdate deployment.
3. The rendered workload still uses `jellyfin-config-local-v1` for `/config`.
4. The migration init container precedes the SSO bootstrap init container.
5. The migration source remains `jellyfin-config-v2` and read-only.
6. GPU selection, authentication references, routes, and resources are
   unchanged.
