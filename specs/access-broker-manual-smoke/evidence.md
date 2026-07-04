# Evidence: access-broker-manual-smoke

**Branch**: `codex/access-broker-manual-smoke`
**Risk Tier**: high
**Started**: 2026-07-04

## Spec Kit Initialization

- Command: manual artifact creation from repo templates.
- Outcome: PASS
- Spec Kit version: existing repo installation
- Integration: Codex
- Fallback: default `/workspaces/homelab-worktrees` path unavailable; used `/home/vscode/homelab-worktrees/access-broker-manual-smoke`.

## Workflow Validation

| Command | Result | Notes |
| ------- | ------ | ----- |
| `python3 tools/codex-harness/validate_sdd_context.py --root "$(pwd)" --branch "$(git branch --show-current)" --require-plan-artifacts` | PASS | Completed with no output. |

## Local Checks

| Command | Result | Notes |
| ------- | ------ | ----- |
| `kubectl kustomize kubernetes/apps/access-broker` | PASS | Render assertion confirmed `onboard.petebeegle.com`, SOPS-encrypted Secret, `nfs-csi-storage`, `ACCESS_STORE_PATH=/data/homelab-access.json`, and no `Ingress`. |
| `kubectl kustomize kubernetes/apps/cloudflare-tunnels` | PASS | Render assertion confirmed Cloudflare ingress for `onboard.petebeegle.com` to `cilium-gateway-public.gateway.svc.cluster.local:80`. |
| `kubectl kustomize kubernetes/clusters/production` | PASS | Render assertion confirmed `app-access-broker`, path `./kubernetes/apps/access-broker`, and dependency on `app-cloudflare-tunnels`. |
| `python3 tools/architecture/render.py --check` | PASS | Initial check reported stale generated docs; `python3 tools/architecture/render.py --write` refreshed `docs/architecture.md`; rerun passed. |
| `rg -n "1523044601429102622\|784726fdbeaf7ad0d59cfdc84ee34c09a322893c59df4b261f4db655461928dd\|replace-me" kubernetes/apps/access-broker/secret.yaml; test $? -eq 1` | PASS | No plaintext Discord app identity or placeholders in encrypted Secret. |
| `rg -n "kind: Ingress" kubernetes/apps/access-broker kubernetes/apps/cloudflare-tunnels kubernetes/clusters/production/apps/access-broker.yaml; test $? -eq 1` | PASS | No Kubernetes `Ingress` added. |

## Automated Smoke And Live Verification

| Target | Method | Result | Notes |
| ------ | ------ | ------ | ----- |
| `https://onboard.petebeegle.com/discord/interactions` | Manual Discord Developer Portal PING | PENDING | Run after app readiness and homelab activation PRs are merged and Flux applies them. |
| Discord `#test` `/access request` | Manual Discord command | PENDING | Run after endpoint validates and slash command is registered. |

## Deployment State

- Source fetched SHA: pending
- Target applied SHA: pending
- Live resource spec checked: pending
- Gateway/listener/DNS/certificate checked: pending
- Exact user-facing URL result: pending

## Development Validation

- Profile: none
- Branch slug: access-broker-manual-smoke
- HEAD: pending
- Report path: N/A
- Cleanup: N/A
- Result or exception: Development cluster omits Cloudflare Tunnel and cannot receive public Discord webhook validation; substitute checks are render, SOPS, route, architecture, and PR checks.

## Documentation Impact

- Updated: SDD artifacts.
- Generated docs: `docs/architecture.md` refreshed for active production app and public hostname.
- No-docs rationale: Manual smoke instructions will be provided in PR/final handoff; durable runbook is deferred until approval/provisioning behavior exists.

## SDD Conformance

- Local sources checked: Spec Kit and implementation runbooks plus binding ADRs listed in spec.
- Upstream Spec Kit sources checked: N/A; no workflow/template changes.
- Spec -> Plan -> Tasks -> Implement alignment: PASS. The spec defines the manual smoke behavior, the plan records the production-smoke exception, tasks trace to requirements, and evidence records local checks.
- Artifact updates after implementation: PASS. Tasks and evidence updated after render and validation checks.

## Exceptions And Follow-Ups

- Exception: production manual smoke is required for Discord public webhook validation.
- Dependency: merge `homelab-access` PR `https://github.com/petebeegle/homelab-access/pull/4` before merging this homelab activation so `ghcr.io/petebeegle/homelab-access:main` has readiness behavior for the current smoke scope.
- Pull request: `https://github.com/petebeegle/homelab/pull/350`
- Follow-up: add channel allowlist after the Discord test channel ID is known.
- Follow-up: add command registration helper or bot-token based registration workflow.

## Final State

- Final branch: codex/access-broker-manual-smoke
- Final HEAD: verify with `git rev-parse HEAD`
- Commit: local commit created; verify with `git rev-parse HEAD`
