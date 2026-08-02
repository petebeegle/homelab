# Bootstrap Interface Contract

## Environment

- `FLUX_BOOTSTRAP_SECRET_PROVIDER`: optional enum `sops|dual|onepassword`; defaults to `sops`.
- `OP_SERVICE_ACCOUNT_TOKEN_REF`: required for `dual` and `onepassword`; must be an `op://` reference.
- `KUBECONFIG`: selects the target cluster using existing kubectl behavior.
- `SOPS_AGE_KEY_FILE`: optional Age key override; defaults to the current operator key path without changing production behavior.

## Command

`terraform/scripts/install-flux-bootstrap-secrets.sh`

The command is idempotent. It creates namespaces client-side with `--dry-run=client`, then applies the selected bootstrap Secret resources. It emits resource/apply status only and never emits resolved values.

## Failures

- Unknown provider modes fail before cluster changes.
- Missing dependencies, references, key files, or empty token reads fail with a concise diagnostic.
- Temporary token files are permission restricted and removed on every exit path.
