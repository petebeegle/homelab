# Evidence: access-broker-authentik-token

**Branch**: `codex/access-broker-authentik-token`
**Date**: 2026-07-04

## Context

- `homelab-access` PR #8 added Authentik user provisioning on approval.
- Live access-broker config already has `AUTHENTIK_BASE_URL`, but its Secret did
  not have `AUTHENTIK_TOKEN`.

## Workflow Notes

- Default worktree path `/workspaces/homelab-worktrees/...` failed with
  permission denied.
- Fallback worktree:
  `/home/vscode/homelab-worktrees/access-broker-authentik-token`.
- Clarify/checklist/analyze skipped because this is a focused secret/config
  rollout for already-merged app behavior.
- Development validation exception: production Discord/Authenik integration is
  required.

## Command Evidence

| Command | Result | Notes |
| ------- | ------ | ----- |
| `sops --decrypt --extract '["stringData"]["AUTHENTIK_BOOTSTRAP_TOKEN"]' kubernetes/infra/authentik/secret.yaml \| jq -Rsa . \| sops set --value-stdin kubernetes/apps/access-broker/secret.yaml '["stringData"]["AUTHENTIK_TOKEN"]'` | PASS | Copied the token between SOPS-managed files without printing the decrypted value. |
| `sops filestatus kubernetes/apps/access-broker/secret.yaml` | PASS | Reported `{"encrypted":true}`. |
| `kubectl kustomize kubernetes/apps/access-broker > /tmp/access-broker-authentik-token-render.yaml && rg -n 'AUTHENTIK_TOKEN\|authentik-user-provisioning\|kind: Ingress' /tmp/access-broker-authentik-token-render.yaml \|\| true` | PASS | Render includes encrypted `AUTHENTIK_TOKEN` and rollout annotation; no rendered `Ingress` line appeared. |
| Plaintext scan for the copied token across `kubernetes/apps/access-broker/secret.yaml` and `specs/access-broker-authentik-token` | PASS | No plaintext match found. |
| `kubectl kustomize kubernetes/clusters/production > /tmp/production-authentik-token-render.yaml && rg -n 'app-access-broker' /tmp/production-authentik-token-render.yaml` | PASS | Production render includes the access-broker Flux Kustomization. |
| No-Ingress scan on access-broker/cloudflare tunnel manifests | PASS | No Kubernetes `Ingress` introduced. |
| `git diff --check` | PASS | No whitespace errors. |

## Secret Handling

- The token is copied between SOPS-encrypted files and must not appear in
  plaintext in committed files or final output.
