# Quickstart: onepassword-prod-foundation

## Prerequisites

Create a production-only read-only service account with access only to `cluster production`. Store its token in the admin-only `cluster bootstrap` item `onepassword-production-operator`, built-in field `credential`. Create a disposable Login item `k8s--onepassword-system--canary` in `cluster production` with a populated built-in password field.

Authenticate the interactive `op` CLI session and verify both references without displaying values. Never export the service-account token into the shell environment.

## Bootstrap and reconcile

Run the existing production bootstrap workflow or invoke `terraform/scripts/install-flux-bootstrap-secrets.sh` with the production kubeconfig, dual provider mode, and the non-secret production reference. Verify only Secret object names and operator readiness.

Push the exact branch, reconcile production through Flux, and record fetched/applied Git revisions. Do not change consumer Secret references.

## Canary

```bash
python3 tools/development/verify_onepassword_operator.py \
  --vault "cluster production" \
  --item k8s--onepassword-system--canary \
  --slug onepassword-prod-foundation \
  --kubeconfig /home/vscode/.kube/homelab-production.config \
  --timeout 10m
```

Expected output contains only the generated Secret resource-version transition, pod UID transition, and cleanup confirmation. If any prerequisite is unavailable, record the blocker and do not begin dual-publish.

## Safety and rollback

Keep `sops-age` and all SOPS consumers active. If operator acceptance fails, suspend/remove only the new production operator Kustomization after preserving diagnostics; existing SOPS consumers continue unchanged. Treat deletion of a durable `OnePasswordItem` as destructive because its generated Secret is also deleted. Automatic cleanup is limited to the disposable canary namespace.
