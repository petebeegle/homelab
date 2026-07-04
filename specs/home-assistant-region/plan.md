# Implementation Plan: home-assistant-region

**Branch**: `codex/home-assistant-region` | **Date**: 2026-07-03 | **Spec**:
`specs/home-assistant-region/spec.md`

**Input**: Feature specification from
`specs/home-assistant-region/spec.md`

## Summary

Configure Home Assistant Home Information through GitOps YAML, keeping exact
location values private through a SOPS-encrypted Kubernetes Secret mounted as
`/config/secrets.yaml`.

## Technical Context

**Risk Tier**: high
**Workflow Tier**: high
**Primary Areas**: Kubernetes, Flux, app configuration, SOPS secrets,
documentation
**Dependencies**: Flux, SOPS/Age, kubectl, Home Assistant YAML secrets
**Storage**: Existing `nfs-csi-storage` PVC unchanged
**Ingress**: Existing Gateway API routes unchanged
**Secrets**: Add `kubernetes/apps/home-assistant/secret.yaml`, encrypted by
SOPS
**Development Validation**: Home Assistant branch profile where available, with
an exception recorded if required cluster access is unavailable

## Constitution Check

*GATE: Must pass before tracked edits and be re-checked before commit.*

- [x] GitOps source of truth preserved; no durable live-cluster-only state.
- [x] No production-first mutation; development validation plan or exception is
      recorded for covered changes.
- [x] Gateway API invariant preserved; no new Kubernetes `Ingress` resources.
- [x] SOPS invariant preserved; no plaintext secret manifests staged.
- [x] NFS default considered for PVC-backed workloads.
- [x] Talos boundary preserved; no SSH-based node operations introduced.
- [x] Sibling clone ownership files validated before tracked edits.
- [x] Documentation impact identified; docs updated or no-docs rationale
      recorded.
- [x] Separate verifier approval required before PR creation.

## Project Structure

### SDD Artifacts

```text
specs/home-assistant-region/
├── spec.md
├── plan.md
├── tasks.md
└── evidence.md
```

### Source Or Documentation Changes

```text
kubernetes/apps/home-assistant/
kubernetes/apps/home-assistant/branch/config/configuration.yaml
kubernetes/clusters/production/apps/home-assistant.yaml
docs/runbooks/home-assistant.md
```

## Tiered TDD And Validation Plan

**TDD expectation**: This is declarative Kubernetes and app configuration.
Focused render checks and SOPS verification are the useful local test seam; live
development validation is required unless infrastructure is unavailable.

**Local checks**:

- `sops -d kubernetes/apps/home-assistant/secret.yaml`
- `kubectl kustomize kubernetes/apps/home-assistant`
- `kubectl kustomize kubernetes/apps/home-assistant/branch`
- `python3 tools/architecture/render.py --check`

**Development smoke**: Run
`python3 tools/development/verify_branch_deploy.py --app home-assistant --branch codex/home-assistant-region --slug home-assistant-region --push`
when cluster credentials and branch deployment prerequisites are available.

**Evidence destination**: `specs/home-assistant-region/evidence.md` and
`.codex/tmp/pr-summary.md`.

## Documentation Impact

Update `docs/runbooks/home-assistant.md` to document YAML-owned Home Information
and SOPS-backed exact location values.

## Implementation Steps

1. Install the staged local Home Assistant coordinate file into the
   implementation clone without logging its contents.
2. Create and immediately encrypt `kubernetes/apps/home-assistant/secret.yaml`.
3. Add production YAML home information and mount `/config/secrets.yaml`.
4. Add Flux SOPS decryption to the production Home Assistant app.
5. Add non-sensitive regional defaults to branch configuration.
6. Update Home Assistant runbook and verification evidence.

## Risks

| Risk | Mitigation |
| ---- | ---------- |
| Plaintext coordinates are committed | Encrypt immediately with SOPS and verify `git diff` shows only encrypted payload fields |
| Flux cannot decrypt the new Secret | Add `spec.decryption` with `sops-age` to the production app Kustomization |
| Home Assistant cannot resolve `!secret` values | Mount the Secret key as `/config/secrets.yaml` beside `configuration.yaml` |
| Development cluster is unavailable | Record exception and substitute SOPS and render checks |

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
| --------- | ---------- | ------------------------------------ |
| N/A | N/A | N/A |
