# Data Model: onepassword-dev-foundation

## Bootstrap Provider Mode

- Values: `sops`, `dual`, `onepassword`.
- Default: `sops` for backward compatibility.
- `sops` requires the existing Age key file.
- `onepassword` requires an authenticated `op` CLI and non-empty secret reference.
- `dual` requires both prerequisite sets and must install both Secrets successfully.

## Operator Trust Root

- Kubernetes identity: `onepassword-system/onepassword-service-account-token`.
- Key: `token`.
- Source: an admin-only `op://` reference resolved at bootstrap.
- Lifecycle: created or updated out of band before Flux reconciles the operator; durable value is never committed or stored in Terraform state.

## Canary Item

- External identity: a manually created item in the development vault.
- Required field: one non-empty built-in `password` field on a disposable Login item.
- Runtime reference: `vaults/<vault-id>/items/<item-id>`.
- Rotation: verifier asks `op item edit --generate-password` to replace the built-in password; the value never enters repository code, command arguments, or output.

## Canary Kubernetes Resources

- Namespace: `onepassword-canary-<slug>`.
- `OnePasswordItem` and generated Secret: `onepassword-canary-<slug>`.
- Deployment: `onepassword-canary-<slug>`, one replica, consumes Secret key `password` through an environment variable.
- Lifecycle: absent by default; applied for smoke; deleted with its namespace unless `--keep` is set.

## Validation State

- Initial Secret resource version.
- Initial active pod UID.
- Rotated Secret resource version, which must differ.
- Rotated active pod UID, which must differ.
- Cleanup result.
- No Secret value is part of validation state or evidence.
