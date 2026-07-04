# Evidence: access-broker-review-admins

**Branch**: `codex/access-broker-review-admins`
**Date**: 2026-07-04

## Context

- `homelab-access` PR #7 adds server-side review admin allowlisting.
- The successful `/access request` smoke identified Discord user
  `252951660027052033` as the initial admin user.

## Workflow Notes

- Default worktree path `/workspaces/homelab-worktrees/...` failed with
  permission denied.
- Fallback worktree:
  `/home/vscode/homelab-worktrees/access-broker-review-admins`.
- Clarify/checklist/analyze skipped because this is a narrow config rollout for
  already-merged app behavior.
- Development validation exception: production Discord guild/app is required.

## Command Evidence

| Command | Result | Notes |
| ------- | ------ | ----- |
| `kubectl kustomize kubernetes/apps/access-broker > /tmp/access-broker-review-admins-render.yaml && rg -n 'DISCORD_ADMIN_USER_IDS\|discord-review-admins\|kind: Ingress' /tmp/access-broker-review-admins-render.yaml \|\| true` | PASS | Render includes admin user ID and rollout annotation; no rendered `Ingress` line appeared. |
| `kubectl kustomize kubernetes/clusters/production > /tmp/production-review-admins-render.yaml && rg -n 'app-access-broker' /tmp/production-review-admins-render.yaml` | PASS | Production render includes the access-broker Flux Kustomization. |
| `(rg -n 'kind: Ingress' kubernetes/apps/access-broker kubernetes/apps/cloudflare-tunnels kubernetes/clusters/production/apps/access-broker.yaml; test $? -eq 1)` | PASS | No Kubernetes `Ingress` introduced. |
| `git diff --check` | PASS | No whitespace errors. |
