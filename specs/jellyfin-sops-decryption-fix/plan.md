# Implementation Plan: Jellyfin SOPS Decryption Fix

**Branch**: `codex/jellyfin-sops-decryption-fix` | **Date**: 2026-08-10 | **Spec**: `specs/jellyfin-sops-decryption-fix/spec.md`

**Input**: Approved prerequisite to correct production Jellyfin SOPS reconciliation before 1Password dual publication.

## Summary

Add the same Flux SOPS decryption configuration used by other production application Kustomizations to `app-jellyfin`. Do not edit credential material or consumers. Gate merge on rendering, policy, no-output committed-value equality, and post-merge exact-revision/live-byte verification.

## Technical Context

**Risk Tier**: high
**Workflow Tier**: high
**Primary Areas**: Flux, Kubernetes, SOPS, Jellyfin OAuth secret handling
**Dependencies**: Flux Kustomization API, existing `flux-system/sops-age`, SOPS CLI, kubectl
**Storage**: Unchanged
**Ingress**: Unchanged
**Secrets**: Existing SOPS/Age documents remain byte-for-byte unchanged
**Smoke Strategy**: No development mutation; production-only reconciliation is verified after merge with exact applied revision plus status-only live byte comparison. Jellyfin SSO acceptance remains required at its later consumer-cutover gate.
**Fanout Targets**: None; the repository change is one file and no agents were requested.
**Development Validation**: Documented exception. Development does not reconcile this production Flux object and its Jellyfin branch profile uses a placeholder secret. Injecting the production credential into development would violate vault/environment isolation and would not test the changed resource.
**Post-Implementation SDD Conformance**: Local full Spec Kit artifacts and convergence; no workflow-standard change.

## Human Gates

**Spec Gate**: Approved by the user on 2026-08-10 after the live ciphertext defect and separate-PR boundary were explained.

**Checklist Status**: `checklists/requirements.md` passes 8/8 requirements-quality checks.

**Plan Gate**: Approved by the same user response because the proposed change, separate PR, and no-output acceptance were stated before approval; this plan introduces no additional design choice.

**Expected Task/Analyze Gate**: Tasks and non-destructive analysis required before implementation; covered by the same explicit approval of the narrowly bounded fix.

## Constitution Check

- [x] GitOps source of truth preserved; no durable live-cluster-only state.
- [x] No production-first mutation; the production-only development exception and substitute checks are recorded.
- [x] Gateway API invariant preserved; no ingress resources change.
- [x] SOPS invariant preserved; no plaintext or encrypted Secret manifest changes.
- [x] NFS default unaffected.
- [x] Talos boundary preserved.
- [x] Branch/worktree match `jellyfin-sops-decryption-fix`.
- [x] Documentation impact is limited to durable SDD evidence; no canonical procedure changes.
- [x] PR review/status checks remain the review gate.

## Project Structure

### SDD Artifacts

```text
specs/jellyfin-sops-decryption-fix/
├── checklists/requirements.md
├── data-model.md
├── evidence.md
├── plan.md
├── quickstart.md
├── research.md
├── spec.md
└── tasks.md
```

### Source Changes

```text
kubernetes/clusters/production/apps/jellyfin.yaml
docs/architecture.md
```

## Tiered TDD And Validation Plan

**TDD expectation**: There is no executable-code seam for a two-field declarative stanza. Before editing, the observed failing state is that rendered `app-jellyfin` has no `.spec.decryption`; after editing, structural assertions require exactly `provider: sops` and `secretRef.name: sops-age`.

**Local checks**:

- Render production and development cluster entrypoints.
- Parse the production render and assert the exact `app-jellyfin` decryption configuration.
- Decrypt the two committed fields into process memory and compare bytes with status-only output.
- Assert encrypted Secret documents and all consumer paths are unchanged.
- Run architecture check, SDD harness, focused policy, unit/harness suites, and full pre-commit.
- Run kubeconform locally if available; otherwise rely on pinned CI 0.7.0 and record the exception.

**Development smoke**: None for the production-only resource, for the isolation reasons above. Existing development Jellyfin branch smoke would validate a placeholder-backed workload, not this reconciliation change.

**Completion evidence**: Record PR/merge SHA, Flux source fetched SHA, `app-jellyfin` applied SHA and Ready state, live decryption configuration, no-output equality, non-envelope check, and workload readiness. Exact SSO login remains outside this prerequisite because the credential is not rotated and consumer configuration is unchanged.

**Fanout plan**: None.

**Evidence destination**: `specs/jellyfin-sops-decryption-fix/evidence.md`.

## Documentation Impact

Regenerate `docs/architecture.md` so its `app-jellyfin` row reports SOPS decryption. No ADR, runbook, README, or procedural documentation changes are required. This restores conformance with the existing SOPS ADR and records discovery/acceptance in the implementation artifacts.

## Implementation Steps

1. Capture the missing-decryption failing assertion and committed-value equality.
2. Add `provider: sops` and `secretRef.name: sops-age` to production `app-jellyfin`.
3. Run broad local validation and diff-scope assertions.
4. Open a gated PR, merge, reconcile exact main, and perform no-output live acceptance.
5. Resume the blocked 1Password dual-publish PR.

## Risks

| Risk | Mitigation |
| ---- | ---------- |
| The Age key cannot decrypt the file | Normal Flux failure blocks readiness; do not proceed to dual publication. |
| The two OAuth sources differ | Local and live status-only comparisons fail closed. |
| Reconciliation changes credential bytes unexpectedly | Secret documents are untouched and both committed plaintexts are proven equal before merge. |
| Sensitive values reach output | Comparisons occur in process memory and print status only; no values, Base64, or hashes are recorded. |

## Complexity Tracking

No constitution violation or additional complexity is introduced.
