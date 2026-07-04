# Evidence: access-broker-oauth-callback

**Branch**: `codex/access-broker-oauth-callback`
**Date**: 2026-07-04

## Context

- `homelab-access` PR #5 merged and adds `GET /oauth/callback`.
- Discord bot token checks showed the bot token is valid for app
  `1523044601429102622`, but the bot is not in guild `1324020069222842378`.
- Official Discord OAuth documentation requires `client_id:client_secret` or
  form `client_secret` for authorization-code token exchange. The bot token
  cannot replace the Client Secret.

## Workflow Notes

- Fallback worktree used:
  `/home/vscode/homelab-worktrees/access-broker-oauth-callback`.
- Default `/workspaces/homelab-worktrees` path was avoided based on prior
  environment failures.
- Clarify/checklist/analyze skipped because the user gave direct implementation
  approval for a narrow manual-smoke unblock and the failing URL identified the
  missing route.
- Development validation exception: Discord production app install and redirect
  URL are bound to `onboard.petebeegle.com`; development does not have an
  equivalent registered app/client secret.

## Command Evidence

| Command | Result | Notes |
| ------- | ------ | ----- |
| `docker run --rm -v "$PWD":/src -w /src golang:1.23 sh -c 'gofmt -w internal/config/config.go internal/server/server.go internal/server/server_test.go && go test ./...'` in `homelab-access` | PASS | Callback app tests passed before PR #5 merge. |
| `gh pr merge 5 --squash --delete-branch` in `homelab-access` | PASS | Merged callback implementation into `petebeegle/homelab-access`. |
| `kubectl kustomize kubernetes/apps/access-broker > /tmp/access-broker-render.yaml && rg -n "DISCORD_REDIRECT_URI\|restarted-for\|imagePullPolicy\|kind: Ingress" /tmp/access-broker-render.yaml \|\| true` | PASS | Render includes `DISCORD_REDIRECT_URI`, rollout annotation, and `imagePullPolicy: Always`; no rendered `Ingress` line appeared. |
| `kubectl kustomize kubernetes/clusters/production > /tmp/production-render.yaml && rg -n "app-access-broker\|DISCORD_REDIRECT_URI\|discord-oauth-callback-2026-07-04" /tmp/production-render.yaml` | PASS | Production cluster render still includes `app-access-broker`; app package content is applied by Flux from its path. |
| `(rg -n "kind: Ingress" kubernetes/apps/access-broker kubernetes/apps/cloudflare-tunnels kubernetes/clusters/production/apps/access-broker.yaml; test $? -eq 1)` | PASS | No Kubernetes `Ingress` introduced. |
| `(rg -n "1523044601429102622\|784726fdbeaf7ad0d59cfdc84ee34c09a322893c59df4b261f4db655461928dd\|MTUyMzA0\|GBtIrX\|DISCORD_CLIENT_SECRET" kubernetes/apps/access-broker; test $? -eq 1)` | PASS | No plaintext Discord app ID, public key, provided bot token prefix, or client-secret key was introduced in access-broker Kubernetes manifests. |

## SDD Conformance

- Spec, plan, tasks, and evidence artifacts exist under one implementation
  directory.
- Plan declares risk tier, workflow tier, smoke strategy, fanout target, and
  development validation exception.
- Converge skipped: the implementation is a two-line manifest follow-up with
  no generated task drift after validation.

## Final State

- Final branch head is recorded by the GitHub PR after push.

## Remaining Requirement

`DISCORD_CLIENT_SECRET` is still required in `access-broker-secret` before the
OAuth callback can exchange Discord's code successfully. This value cannot be
derived from the bot token, public key, or app ID.
