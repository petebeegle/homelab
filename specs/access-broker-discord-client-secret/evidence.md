# Evidence: access-broker-discord-client-secret

**Branch**: `codex/access-broker-discord-client-secret`
**Date**: 2026-07-04

## Context

- Public `/oauth/callback` already routes to access-broker.
- Latest smoke returns broker JSON error `discord client secret is not
  configured`.
- The user provided the Discord Client Secret out-of-band in chat.

## Workflow Notes

- Default worktree path `/workspaces/homelab-worktrees/...` failed with
  permission denied.
- Fallback worktree:
  `/home/vscode/homelab-worktrees/access-broker-discord-client-secret`.
- Clarify/checklist/analyze skipped because this is a focused SOPS secret
  unblock with direct user approval.
- Development validation exception: production Discord OAuth app and public
  callback hostname are the tested integration.

## Command Evidence

| Command | Result | Notes |
| ------- | ------ | ----- |
| `sops set --value-stdin kubernetes/apps/access-broker/secret.yaml '["stringData"]["DISCORD_CLIENT_SECRET"]'` | PASS | Added the provided value as SOPS-encrypted data. Initial PTY attempt echoed stdin and failed because SOPS expects JSON; successful run used a JSON string. |
| `sops filestatus kubernetes/apps/access-broker/secret.yaml` | PASS | Reported `{"encrypted":true}`. |
| `kubectl kustomize kubernetes/apps/access-broker >/tmp/access-broker-secret-render.yaml && rg -n 'DISCORD_CLIENT_SECRET\|kind: Ingress' /tmp/access-broker-secret-render.yaml \|\| true` | PASS | Render includes encrypted `DISCORD_CLIENT_SECRET`; no rendered `Ingress` line appeared. |
| Plaintext scan for provided client secret across `kubernetes/apps/access-broker/secret.yaml` and `specs/access-broker-discord-client-secret` | PASS | No plaintext match found. |
| `git diff -- kubernetes/apps/access-broker/secret.yaml` | PASS | Diff shows only encrypted `DISCORD_CLIENT_SECRET` plus SOPS metadata updates. |

## Secret Handling

- The secret value was added with SOPS and must not appear in plaintext in the
  committed manifest or final answer.
