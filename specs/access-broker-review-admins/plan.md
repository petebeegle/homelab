# Implementation Plan: access-broker-review-admins

**Branch**: `codex/access-broker-review-admins` | **Date**: 2026-07-04 |
**Spec**: `specs/access-broker-review-admins/spec.md`

## Summary

Add `DISCORD_ADMIN_USER_IDS` to the access-broker ConfigMap and update the
Deployment rollout annotation to load the new image/config.

## Technical Context

**Risk Tier**: medium
**Workflow Tier**: medium
**Primary Areas**: Kubernetes app config, Flux GitOps
**Dependencies**: Flux, kubectl/kustomize, homelab-access PR #7
**Storage**: Existing PVC unchanged
**Ingress**: Existing Gateway API unchanged
**Secrets**: No secret change; Discord user ID is not secret
**Smoke Strategy**: Manual Discord command smoke after deploy
**Fanout Targets**: Render and live verification are independent after merge
**Development Validation**: Exception; production Discord guild/app is the test
surface.
**Post-Implementation SDD Conformance**: Recorded in evidence.

## Human Gates

**Spec Gate**: Approved by ongoing user instruction.
**Checklist Status**: Skipped; narrow config rollout.
**Plan Gate**: Approved by ongoing user instruction.
**Expected Task/Analyze Gate**: Analyze skipped with evidence rationale.

## Constitution Check

- [x] GitOps source of truth preserved.
- [x] Development validation exception recorded.
- [x] Gateway API invariant unaffected.
- [x] SOPS invariant unaffected.
- [x] Branch/worktree mode recorded.

## Project Structure

```text
specs/access-broker-review-admins/
├── spec.md
├── plan.md
├── tasks.md
└── evidence.md

kubernetes/apps/access-broker/configmap.yaml
kubernetes/apps/access-broker/deployment.yaml
```

## Tiered TDD And Validation Plan

**Local checks**:

- `kubectl kustomize kubernetes/apps/access-broker`
- `kubectl kustomize kubernetes/clusters/production`
- no-`Ingress` scan

**Development smoke**: Exception; production Discord guild/app is required.

**Evidence destination**: `specs/access-broker-review-admins/evidence.md`.

## Risks

| Risk | Mitigation |
| ---- | ---------- |
| Mutable `main` image not updated at rollout time | Wait for homelab-access image CI before restarting pod |
