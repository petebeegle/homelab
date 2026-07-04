# Implementation Plan: access-broker-authentik-token

**Branch**: `codex/access-broker-authentik-token` | **Date**: 2026-07-04 |
**Spec**: `specs/access-broker-authentik-token/spec.md`

## Summary

Copy the existing Authentik bootstrap token into access-broker's SOPS Secret as
`AUTHENTIK_TOKEN` and update the rollout annotation so the new app image/config
is loaded.

## Technical Context

**Risk Tier**: medium
**Workflow Tier**: medium
**Primary Areas**: Kubernetes Secret, SOPS, Flux GitOps
**Dependencies**: SOPS, Flux, kubectl/kustomize, homelab-access PR #8
**Storage**: Existing PVC unchanged
**Ingress**: Existing Gateway API unchanged
**Secrets**: SOPS-encrypted `kubernetes/apps/access-broker/secret.yaml`
**Smoke Strategy**: Manual Discord approve smoke after deploy
**Fanout Targets**: SOPS/render scans are independent
**Development Validation**: Exception; production Discord/Authenik integration
is the tested surface.
**Post-Implementation SDD Conformance**: Recorded in evidence.

## Human Gates

**Spec Gate**: Approved by ongoing user instruction.
**Checklist Status**: Skipped; focused secret rollout.
**Plan Gate**: Approved by ongoing user instruction.
**Expected Task/Analyze Gate**: Analyze skipped with evidence rationale.

## Constitution Check

- [x] GitOps source of truth preserved.
- [x] Development validation exception recorded.
- [x] Gateway API invariant unaffected.
- [x] SOPS invariant preserved; no plaintext secret committed.
- [x] Branch/worktree mode recorded.

## Project Structure

```text
specs/access-broker-authentik-token/
├── spec.md
├── plan.md
├── tasks.md
└── evidence.md

kubernetes/apps/access-broker/secret.yaml
kubernetes/apps/access-broker/deployment.yaml
```

## Tiered TDD And Validation Plan

**Local checks**:

- `sops filestatus kubernetes/apps/access-broker/secret.yaml`
- `kubectl kustomize kubernetes/apps/access-broker`
- plaintext token scan
- no-`Ingress` scan

**Development smoke**: Exception; production Discord/Authenik integration is
required.

**Evidence destination**: `specs/access-broker-authentik-token/evidence.md`.

## Risks

| Risk | Mitigation |
| ---- | ---------- |
| Token committed in plaintext | Use `sops set --value-stdin`; scan before commit |
| Mutable image rollout happens before image publish | Confirm `homelab-access:main` digest after app CI |
