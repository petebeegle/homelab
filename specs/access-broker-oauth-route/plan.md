# Implementation Plan: access-broker-oauth-route

**Branch**: `codex/access-broker-oauth-route` | **Date**: 2026-07-04 |
**Spec**: `specs/access-broker-oauth-route/spec.md`

## Summary

Add the missing Gateway API HTTPRoute match for `/oauth/callback` and verify the
public path reaches access-broker.

## Technical Context

**Risk Tier**: medium
**Workflow Tier**: medium
**Primary Areas**: Kubernetes Gateway API, Flux GitOps
**Dependencies**: Flux, kubectl/kustomize
**Storage**: N/A
**Ingress**: Gateway API HTTPRoute only
**Secrets**: No secret changes
**Smoke Strategy**: Scriptable public URL smoke
**Fanout Targets**: Render and public smoke are independent after merge
**Development Validation**: Exception; the failing path is production
Cloudflare/Gateway routing for `onboard.petebeegle.com`.
**Post-Implementation SDD Conformance**: Recorded in evidence.

## Human Gates

**Spec Gate**: Approved by ongoing user implementation instruction.
**Checklist Status**: Skipped; one-path route fix.
**Plan Gate**: Approved by ongoing user implementation instruction.
**Expected Task/Analyze Gate**: Analyze skipped with evidence rationale.

## Constitution Check

- [x] GitOps source of truth preserved.
- [x] Development validation exception recorded.
- [x] Gateway API invariant preserved; no Kubernetes `Ingress`.
- [x] SOPS invariant preserved; no secret edits.
- [x] Branch/worktree mode recorded.

## Project Structure

```text
specs/access-broker-oauth-route/
├── spec.md
├── plan.md
├── tasks.md
└── evidence.md

kubernetes/apps/access-broker/httproute.yaml
```

## Tiered TDD And Validation Plan

**Local checks**:

- `kubectl kustomize kubernetes/apps/access-broker`
- `kubectl kustomize kubernetes/clusters/production`
- no-`Ingress` scan

**Development smoke**: Exception; use production public URL smoke after merge.

**Evidence destination**: `specs/access-broker-oauth-route/evidence.md`.

## Risks

| Risk | Mitigation |
| ---- | ---------- |
| Public smoke still fails due stale Gateway status | Verify Flux apply and live HTTPRoute generation/status |
