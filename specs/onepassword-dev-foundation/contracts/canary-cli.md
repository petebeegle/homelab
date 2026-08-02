# Canary Verifier CLI Contract

## Command

`python3 tools/development/verify_onepassword_operator.py --vault <vault> --item <item> --slug <slug>`

## Options

- `--kubeconfig <path>`: defaults to `~/.kube/homelab-development.config`.
- `--timeout <duration>`: defaults to `15m` and must cover two 300-second polls.
- `--keep`: retain the temporary namespace for debugging; default is cleanup.
- `--skip-rotation`: prove initial sync only; not acceptable for final phase evidence.

## Preconditions

- Authenticated `op` CLI access to the development vault and permission to edit the canary item.
- Canary item is a Login item containing a non-empty built-in `password` field.
- Development operator Kustomization and HelmRelease are Ready.

## Output

Only resource versions, pod UIDs, and cleanup outcomes may be printed. Item contents, generated random values, operator tokens, and Kubernetes Secret data are prohibited.

## Exit Status

- `0`: initial sync, rotation/restart when enabled, and cleanup all pass.
- Non-zero: prerequisite, rendering, reconciliation, rotation, timeout, or cleanup failure. Cleanup is still attempted unless `--keep` is set.
