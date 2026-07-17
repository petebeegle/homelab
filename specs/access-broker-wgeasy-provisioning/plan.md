# Implementation Plan: access-broker-wgeasy-provisioning

**Branch**: `codex/access-broker-wgeasy-provisioning`
**Date**: 2026-07-17
**Spec**: `specs/access-broker-wgeasy-provisioning/spec.md`

## Summary

Apply the smallest Kubernetes desired-state change needed after
`homelab-access` PR #9: explicit wg-easy username config plus a pod-template
annotation bump to pull the newly published mutable `main` image.

## Technical Context

**SDD tier**: medium
**Workflow risk tier**: medium
**Smoke strategy**: render checks plus documented live-smoke blocker; manual
approval smoke requires a SOPS-encrypted `WGEASY_PASSWORD`.
**Fanout targets**: read-only image workflow verification and manifest render
validation can run independently; tracked edits stay sequential.
**Worktree exception**: `/workspaces/homelab-worktrees` is unavailable; using
`/home/vscode/homelab-worktrees/access-broker-wgeasy-provisioning`.

## Risks

| Risk | Mitigation |
| --- | --- |
| Mutable `main` image not published when Flux rolls | Confirm main image workflow passed before annotation bump |
| Missing wg-easy password makes approval fail at VPN step | Record as live-smoke blocker and do not invent a secret value |
| Secret leakage | Do not print or commit plaintext credentials; scan tracked files |

## Validation

- `kubectl kustomize kubernetes/apps/access-broker`
- `kubectl kustomize kubernetes/clusters/production`
- plaintext scan for `WGEASY_PASSWORD` and known secret-shaped values
- SDD context validation

## Exceptions

Clarify, checklist, analyze, and converge are treated as lightweight/skipped
because this is a narrow manifest rollout after a merged app PR; rationale and
results are recorded in `evidence.md`.
