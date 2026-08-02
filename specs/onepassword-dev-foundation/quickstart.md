# Quickstart: 1Password Development Foundation

## Prerequisites

1. Rebuild the devcontainer so pinned `op` is available.
2. Authenticate `op` to the administrator account.
3. Create the `Homelab Development` vault, a read-only development operator service account, and an admin-only bootstrap item containing its token.
4. Create a disposable Login canary item in the development vault with a non-empty built-in `password` field; the validating human identity must be allowed to edit it.
5. Ensure `~/.kube/homelab-development.config` and the existing Age key are available.

## Local Validation

Run the focused tests and render commands listed in `plan.md`. Render the official chart with the committed values and assert that only the operator Deployment is present—no Connect API/sync Deployment or token-valued Secret.

## Install Dual Bootstrap Secrets

Run the bootstrap-secret helper directly against the existing development cluster with provider mode `dual` and the documented bootstrap `op://` reference. Do not paste or export the token itself.

## Reconcile Development Base

Push the exact branch and run the whoami development verifier with `--include-cluster-base`. Confirm the `onepassword-operator` Flux Kustomization and HelmRelease are Ready before canary validation.

## Run Canary

Run `verify_onepassword_operator.py` with the canary vault/item titles and a DNS-safe slug. The verifier resolves IDs, creates temporary resources, observes initial readiness, rotates the disposable field, waits for Secret and pod identity changes, and deletes the namespace.

Expected output includes only Secret resource-version and pod-UID transitions plus a successful cleanup statement. If credentials or infrastructure are unavailable, record the exact blocker in `evidence.md` and do not begin `onepassword-prod-foundation`.
