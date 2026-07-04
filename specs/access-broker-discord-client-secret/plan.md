# Implementation Plan: access-broker-discord-client-secret

**Branch**: `codex/access-broker-discord-client-secret` | **Date**: 2026-07-04 |
**Spec**: `specs/access-broker-discord-client-secret/spec.md`

## Summary

Use `sops set --value-stdin` to add `DISCORD_CLIENT_SECRET` to the access-broker
Secret, then validate that the committed manifest remains encrypted and deploy
through Flux.

## Technical Context

**Risk Tier**: medium
**Workflow Tier**: medium
**Primary Areas**: Kubernetes Secret, SOPS, Flux GitOps
**Dependencies**: SOPS, Flux, kubectl/kustomize
**Storage**: N/A
**Ingress**: Existing Gateway API unchanged
**Secrets**: SOPS-encrypted `kubernetes/apps/access-broker/secret.yaml`
**Smoke Strategy**: Scriptable public callback smoke after deployment
**Fanout Targets**: Render and SOPS scans are independent
**Development Validation**: Exception; production Discord OAuth app and callback
hostname are the tested integration.
**Post-Implementation SDD Conformance**: Recorded in evidence.

## Human Gates

**Spec Gate**: Approved by direct user instruction.
**Checklist Status**: Skipped; focused secret unblock.
**Plan Gate**: Approved by direct user instruction.
**Expected Task/Analyze Gate**: Analyze skipped with evidence rationale.

## Constitution Check

- [x] GitOps source of truth preserved.
- [x] Development validation exception recorded.
- [x] Gateway API invariant unaffected.
- [x] SOPS invariant preserved; no plaintext Secret committed.
- [x] Branch/worktree mode recorded.

## Project Structure

```text
specs/access-broker-discord-client-secret/
├── spec.md
├── plan.md
├── tasks.md
└── evidence.md

kubernetes/apps/access-broker/secret.yaml
```

## Tiered TDD And Validation Plan

**Local checks**:

- `sops filestatus kubernetes/apps/access-broker/secret.yaml`
- `kubectl kustomize kubernetes/apps/access-broker`
- plaintext secret scan

**Development smoke**: Exception; use production callback smoke after merge.

**Evidence destination**:
`specs/access-broker-discord-client-secret/evidence.md`.

## Risks

| Risk | Mitigation |
| ---- | ---------- |
| Secret committed in plaintext | Use `sops set --value-stdin`; scan manifest before commit |
