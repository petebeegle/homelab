# Finish the 1Password migration

Date: 2026-11-16. Status: proposed, awaiting owner approval.

## Intent

Production runs two secret systems. Seventeen 1Password items are synced into
the cluster beside sixteen SOPS files, and every workload still reads the SOPS
copy, so each secret change has to be made twice. The owner has chosen
1Password as the single system. This finishes the move and removes SOPS.

## Where things stand

- `tools/onepassword/validate_secret_parity.py` against production on
  2026-11-16: 16 of 17 pairs match byte for byte.
- The one mismatch is `wireguard/wireguard-env`, key `WG_HOST`. The SOPS file
  was updated on 2026-10-03; the 1Password item was created on 2026-08-10 and
  is stale.
- Development already reads 1Password. Two development Kustomizations still
  have SOPS decryption switched on (cert-manager and the Immich branch
  template).
- Production polls 17 items hourly, about 410 requests a day against a limit of
  1,000.

## Goals

- Every production workload reads its secret from a `OnePasswordItem`.
- No SOPS-encrypted files, decryption settings, or SOPS tooling remain.
- One documented way to add or rotate a secret.

## Non-goals

- Rotating any secret value.
- Changing Terraform's own sensitive variables (`terraform.tfvars`).
- Moving Terraform state (issue #486).

## Approaches

1. **Repoint each workload to the `-onepassword` Secret and delete the SOPS
   file in the same PR.** Chosen. The target Secret already exists and has been
   proven identical, so the pod restarts onto the same values with no gap.
   Reverting the PR restores the old wiring while `sops-age` is still in the
   cluster. Cost: the `-onepassword` suffix stays in Secret names.
2. Rename each `OnePasswordItem` to the legacy Secret name. Keeps the old
   names, but the operator and Flux's prune would both act on the same Secret
   during the switch, and a lost race deletes a Secret a running pod needs.
3. Big-bang switch in one PR. Fewest PRs, but one bad reference takes down
   several apps at once and the revert is all or nothing.

Development proves the pattern: cert-manager there already reads
`cloudflare-api-token-onepassword`.

## Design

**Order.** One PR per batch, lowest stakes first. Each batch is merged only
after the previous one is verified.

| Batch | Secrets |
|-------|---------|
| 1 | valheim, pihole, renovate |
| 2 | foundryvtt, access-broker, cloudflare tunnels, home-assistant, jellyfin, immich (two secrets) |
| 3 | grafana credentials, grafana-env in `grafana` and `monitoring` |
| 4 | wireguard (after the item is corrected), authentik, cert-manager, the private-repo deploy key |

**Per secret.** Change every reference from the legacy name to the
`-onepassword` name, delete the SOPS file and its kustomization entry, and
drop `decryption:` from that app's Flux Kustomization when it has no SOPS files
left.

**Verification per batch.** Before merge: rerun the parity tool. After merge:
the Flux Kustomization is Ready, the workload has rolled out, the pod mounts or
reads the new Secret name, and the app's own route or function works (login
page, DNS answer, tunnel up, certificate still issuing). Record this in the PR.

**Removing SOPS (final PR).** Delete `.sops.yaml`, the SOPS guard hook and its
wiring in `.codex/config.toml` and `.claude/settings.json`, the SOPS-specific
CI secrets check, and the remaining `decryption:` blocks in both clusters.
Switch bootstrap from `dual` to 1Password only in
`terraform/production/main.tf`, `terraform/development/main.tf` and
`terraform/scripts/install-flux-bootstrap-secrets.sh`, and update
`tools/policy/check_onepassword_production_foundation.py` to match. Add a
check that fails if a Kubernetes `Secret` manifest is committed at all.
GitGuardian stays.

**Records.** A new decision record supersedes
`docs/decisions/sops-age-secrets.md`. `AGENTS.md`, `README.md`,
`docs/runbooks/add-secret.md`, `add-app.md`, `onepassword-operator.md`,
`docs/overview.md` and the two matching skills are rewritten for 1Password.

## Constraints

- No secret value is printed, logged, pasted, or passed as a shell argument.
- Production is changed only through merged PRs.
- `sops-age` stays in the production cluster until the final PR is verified, so
  any batch can be reverted.

## Owner actions

- Correct `WG_HOST` in the 1Password item `k8s--wireguard--wireguard-env` to
  the value now in production. Batch 4 waits for parity to pass.
- Keep a copy of the age key outside the cluster. Old commits stay encrypted
  with it.
- Run `terraform apply` for the bootstrap change if a plan shows one. It only
  matters for a future rebuild.

## What is left to the builder

- The exact reference edits per app; the full list of references is in the
  repo under the legacy names in `tools/onepassword/production_items.json`.
- Whether the Immich and Jellyfin development branch templates need matching
  edits.
- The shape of the "no Secret manifests" check.

## Risk accepted

After this, a cluster cannot start workloads without reaching 1Password and
holding the service-account token. The rebuild runbook in #486 must cover
where that token lives and the order of bootstrap.
