# Data Model: onepassword-dev-cutover

- Cert-manager item: Opaque, `token`, generated `cloudflare-api-token-onepassword`.
- Immich configuration item: Opaque, `immich-config.yaml`, generated `immich-secrets-onepassword`.
- Immich database item: `kubernetes.io/basic-auth`, `password` and `username`, generated `immich-postgres-user-onepassword`.
- Outage evidence: Secret UID/resourceVersion/data digest held only in memory; workload UID/readiness; cleanup/recovery state.
