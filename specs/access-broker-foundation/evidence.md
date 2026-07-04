# Evidence: access-broker-foundation

**Branch**: `codex/access-broker-foundation`
**Risk Tier**: high
**Started**: 2026-07-04

## Spec Kit Initialization

- Command: manual artifact creation from repo templates after user requested implementation.
- Outcome: PASS
- Spec Kit version: not changed
- Integration: existing Codex integration
- Fallback: default `/workspaces/homelab-worktrees` path was unavailable due to permissions; used `/home/vscode/homelab-worktrees/access-broker-foundation`.

## Workflow Validation

| Command | Result | Notes |
| ------- | ------ | ----- |
| `python3 tools/codex-harness/validate_sdd_context.py --root "$(pwd)" --branch "$(git branch --show-current)" --require-plan-artifacts` | PASS | Completed with no output on branch `codex/access-broker-foundation`. |

## App Repository Checks

| Command | Result | Notes |
| ------- | ------ | ----- |
| `docker run --rm -v "$PWD":/src -w /src golang:1.23-alpine go test ./...` | PASS | Ran in `/home/vscode/homelab-access`; host Go is unavailable, so validation used the Go container. |
| `docker build -t homelab-access:foundation .` | PASS | Built the foundation image successfully in `/home/vscode/homelab-access`. |
| `git commit -m "feat: bootstrap homelab access broker"` | PASS | App repo branch `codex/access-broker-foundation` committed as `252c7bf68bc15ba97430836e80808f1ef291600f` after initializing app repo `main` and rebasing the feature branch. |

## Local Checks

| Command | Result | Notes |
| ------- | ------ | ----- |
| `kubectl kustomize kubernetes/apps/access-broker` | PASS | Rendered Namespace, ConfigMap, SOPS-encrypted Secret, Service, PVC, Deployment, and HTTPRoute. |
| `python3 tools/architecture/render.py --check` | PASS | Initial check reported stale generated docs; `python3 tools/architecture/render.py --write` refreshed `docs/architecture.md`; rerun passed. |
| `rg -n "replace-me\|DISCORD_BOT_TOKEN: [^E]\|AUTHENTIK_TOKEN: [^E]\|WGEASY_PASSWORD: [^E]" kubernetes/apps/access-broker/secret.yaml specs/access-broker-foundation kubernetes/apps/access-broker` | PASS | No plaintext placeholder or unencrypted secret values found. |
| `kubectl kustomize kubernetes/apps/access-broker >/tmp/access-broker-render.yaml && python3 - <<'PY' ... PY` | PASS | Confirmed HTTPRoute present, SOPS encrypted secret present, PVC uses `nfs-csi-storage`, `fsGroup: 65532` is set, and rendered package contains no `kind: Ingress`. |
| `rg -n "access-broker\|kind: Ingress\|apiVersion: networking.k8s.io/v1" kubernetes/clusters kubernetes/apps/access-broker kubernetes/apps/cloudflare-tunnels` | PASS | `access-broker` appears only in the inactive app package; no cluster activation reference or Cloudflare rule was added. Existing Flux NetworkPolicy API strings are unrelated. |

## Automated Smoke And Live Verification

| Target | Method | Result | Notes |
| ------ | ------ | ------ | ----- |
| access-broker live deployment | none | SKIP | The app package is intentionally inactive; no Flux Kustomization or Cloudflare Tunnel rule is activated in this foundation PR. |

## Deployment State

- Source fetched SHA: N/A; inactive package only.
- Target applied SHA: N/A; inactive package only.
- Live resource spec checked: N/A; inactive package only.
- Gateway/listener/DNS/certificate checked: N/A; route contract renders only.
- Exact user-facing URL result: N/A; no live route.

## Development Validation

- Profile: none
- Branch slug: access-broker-foundation
- HEAD: pending
- Report path: N/A
- Cleanup: N/A
- Result or exception: Development smoke skipped because this PR does not activate Flux, Cloudflare Tunnel, or a live route. Substitute checks are app tests/build and Kubernetes render checks.

## Documentation Impact

- Updated: SDD artifacts under `specs/access-broker-foundation/`.
- Generated docs: `docs/architecture.md` refreshed because the generated inventory includes the inactive app package.
- No-docs rationale: Runtime operator runbook is deferred until live Discord/Auth/wg-easy behavior exists.

## SDD Conformance

- Local sources checked: `docs/runbooks/spec-driven-development.md`, `docs/runbooks/implementation-workflow.md`, binding ADRs listed in spec.
- Upstream Spec Kit sources checked: N/A; no Spec Kit template or workflow changes.
- Spec -> Plan -> Tasks -> Implement alignment: PASS. The spec defines the foundation scope, the plan records the inactive deployment strategy, tasks trace to requirements, and evidence records checks and exceptions.
- Artifact updates after implementation: PASS. Tasks and evidence were updated after implementation and validation.

## Exceptions And Follow-Ups

- Follow-up: commit and push `/home/vscode/homelab-access` to initialize `https://github.com/petebeegle/homelab-access`.
- Follow-up: implement Discord interactions in `homelab-access`.
- Follow-up: implement Authentik invite/group client in `homelab-access`.
- Follow-up: implement wg-easy v15.3.0 adapter in `homelab-access`.
- Follow-up: activate Cloudflare Tunnel and Flux only after real credentials and one-time download implementation exist.

## Final State

- Final branch: codex/access-broker-foundation
- Final HEAD: not recorded in committed evidence to avoid a self-referential amend loop; verify with `git rev-parse HEAD` during handoff.
- Commit: local commit created; verify with `git rev-parse HEAD` during handoff.
- Pull requests: `https://github.com/petebeegle/homelab-access/pull/1` and `https://github.com/petebeegle/homelab/pull/346`.
