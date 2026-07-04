# Evidence: access-broker-oauth-route

**Branch**: `codex/access-broker-oauth-route`
**Date**: 2026-07-04

## Context

- PR #353 deployed callback-capable access-broker config and rolled the pod.
- Public smoke still returned Cloudflare 404 for `/oauth/callback`.
- Live HTTPRoute inspection showed matches only for `/download/` and
  `/discord/interactions`.

## Workflow Notes

- Fallback worktree:
  `/home/vscode/homelab-worktrees/access-broker-oauth-route`.
- Clarify/checklist/analyze skipped because this is a one-path route correction
  discovered during live smoke.
- Development validation exception: production Cloudflare hostname/Gateway path
  is the tested surface.

## Command Evidence

| Command | Result | Notes |
| ------- | ------ | ----- |
| `kubectl kustomize kubernetes/apps/access-broker > /tmp/access-broker-route-render.yaml && rg -n "/oauth/callback\|kind: Ingress" /tmp/access-broker-route-render.yaml \|\| true` | PASS | Render includes `/oauth/callback`; no rendered `Ingress` line appeared. |
| `kubectl kustomize kubernetes/clusters/production > /tmp/production-route-render.yaml && rg -n "app-access-broker" /tmp/production-route-render.yaml` | PASS | Production render includes the access-broker Flux Kustomization. |
| `(rg -n "kind: Ingress" kubernetes/apps/access-broker kubernetes/apps/cloudflare-tunnels kubernetes/clusters/production/apps/access-broker.yaml; test $? -eq 1)` | PASS | No Kubernetes `Ingress` introduced. |
| `git diff --check` | PASS | No whitespace errors. |

## Remaining Requirement

After routing is fixed, `DISCORD_CLIENT_SECRET` is still required for a real
Discord OAuth code exchange.
