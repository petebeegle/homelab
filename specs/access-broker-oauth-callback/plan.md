# Implementation Plan: access-broker-oauth-callback

**Branch**: `codex/access-broker-oauth-callback` | **Date**: 2026-07-04 |
**Spec**: `specs/access-broker-oauth-callback/spec.md`

**Input**: Feature specification from
`specs/access-broker-oauth-callback/spec.md`

## Summary

Wire the production access-broker deployment to the Discord OAuth callback URL
and force a Pod rollout so the merged `homelab-access` callback code is pulled
from `ghcr.io/petebeegle/homelab-access:main`.

## Technical Context

**Risk Tier**: medium
**Workflow Tier**: medium
**Primary Areas**: Kubernetes app config, Flux GitOps, Discord OAuth smoke
**Dependencies**: Flux, kubectl/kustomize, merged `homelab-access` PR #5
**Storage**: Existing `nfs-csi-storage` PVC unchanged
**Ingress**: Existing Gateway API HTTPRoute and Cloudflare Tunnel unchanged
**Secrets**: Existing SOPS Secret unchanged; `DISCORD_CLIENT_SECRET` remains
required and cannot be committed without the real secret value
**Smoke Strategy**: Scriptable public URL smoke after deployment
**Fanout Targets**: Render checks and live read-only verification can run
independently after merge
**Development Validation**: Exception. This is a production Discord application
install callback tied to `onboard.petebeegle.com`; development lacks the app
registration, client secret, and Discord redirect configuration.
**Post-Implementation SDD Conformance**: Local workflow review recorded in
evidence.

## Human Gates

**Spec Gate**: Approved by direct user implementation instruction.

**Checklist Status**: Skipped; narrow urgent smoke unblock with clear acceptance.

**Plan Gate**: Approved by direct user implementation instruction.

**Expected Task/Analyze Gate**: Analyze skipped with rationale recorded in
evidence; task list is short and traceable.

## Constitution Check

- [x] GitOps source of truth preserved; no durable live-cluster-only state.
- [x] No production-first mutation; development validation exception recorded.
- [x] Gateway API invariant preserved; no new Kubernetes `Ingress` resources.
- [x] SOPS invariant preserved; no plaintext secret manifests staged.
- [x] NFS default considered for PVC-backed workloads; unchanged.
- [x] Talos boundary preserved; no SSH-based node operations introduced.
- [x] Branch is `codex/access-broker-oauth-callback`; fallback worktree path is
      recorded.
- [x] Documentation impact identified; existing access-broker docs/spec evidence
      are sufficient.
- [x] PR review/status checks are the review gate.

## Project Structure

### SDD Artifacts

```text
specs/access-broker-oauth-callback/
├── spec.md
├── plan.md
├── tasks.md
└── evidence.md
```

### Source Or Documentation Changes

```text
kubernetes/apps/access-broker/configmap.yaml
kubernetes/apps/access-broker/deployment.yaml
specs/access-broker-oauth-callback/
```

## Tiered TDD And Validation Plan

**TDD expectation**: No executable code in this repo. Validate by kustomize
render assertions and post-merge live HTTP smoke.

**Local checks**:

- `kubectl kustomize kubernetes/apps/access-broker`
- `kubectl kustomize kubernetes/clusters/production`
- `rg -n "kind: Ingress" kubernetes/apps/access-broker`

**Development smoke**: Exception as above.

**Completion evidence**: Record PR merge SHA, Flux-applied SHA, live Deployment
spec, and public `/oauth/callback` HTTP result.

**Fanout plan**: Render validation and live status checks are independent and
consolidated into `evidence.md`.

**Evidence destination**:
`specs/access-broker-oauth-callback/evidence.md`.

## Documentation Impact

No generated architecture change expected; app topology and routes are
unchanged.

## Implementation Steps

1. Add `DISCORD_REDIRECT_URI` to the access-broker ConfigMap.
2. Add a Pod-template rollout annotation for the OAuth callback rollout.
3. Run render checks and record evidence.
4. Commit, push, PR, merge, and verify Flux/live HTTP behavior.

## Risks

| Risk | Mitigation |
| ---- | ---------- |
| Callback still cannot complete exchange without client secret | Record explicit remaining requirement and avoid committing fake secret data |
| Mutable `:main` image is cached | Deployment already has `imagePullPolicy: Always`; Pod template annotation forces rollout |
