# Implementation Plan: home-assistant-automation-yaml-writable

**Branch**: `codex/home-assistant-automation-yaml-writable` | **Date**: 2026-07-04 | **Spec**:
`specs/home-assistant-automation-yaml-writable/spec.md`

**Input**: Feature specification from `specs/home-assistant-automation-yaml-writable/spec.md`

## Summary

Remove Home Assistant's read-only ConfigMap ownership of `automations.yaml` so UI saves can atomically replace the file on the writable config PVC. Seed fresh PVCs with a valid empty automation list from the existing init-container path and document the invariant in the Home Assistant runbook.

## Technical Context

**Risk Tier**: medium
**Workflow Tier**: medium
**Primary Areas**: Kubernetes manifests, Home Assistant app behavior, branch overlay, documentation, Spec Kit artifacts
**Dependencies**: kubectl kustomize, Python architecture renderer, Codex harness validators, development smoke tooling
**Storage**: `/config` remains backed by the `home-assistant-config` PVC using `nfs-csi-storage`
**Ingress**: Existing Gateway API routes are unchanged
**Secrets**: SOPS secret manifests are unchanged
**Smoke Strategy**: Run the Home Assistant development branch smoke profile with `--push` and kubeconfig `~/.kube/homelab-development.config` if feasible after staging smoke secrets
**Fanout Targets**: Read-only render/source checks and documentation/evidence review can run independently after implementation edits
**Development Validation**: `python3 tools/development/verify_branch_deploy.py --app home-assistant --branch codex/home-assistant-automation-yaml-writable --slug home-assistant-automation-yaml-writable --kubeconfig ~/.kube/homelab-development.config --push`
**Post-Implementation SDD Conformance**: Local Spec Kit workflow/runbook conformance only

## Constitution Check

*GATE: Must pass before tracked edits and be re-checked before commit.*

- [x] GitOps source of truth preserved; no durable live-cluster-only state.
- [x] No production-first mutation; development validation plan or exception is recorded for covered changes.
- [x] Gateway API invariant preserved; no new Kubernetes `Ingress` resources.
- [x] SOPS invariant preserved; no plaintext secret manifests staged.
- [x] NFS default considered for PVC-backed workloads.
- [x] Talos boundary preserved; no SSH-based node operations introduced.
- [x] Branch is `codex/home-assistant-automation-yaml-writable`; current checkout path is intentionally `/workspaces/homelab-ideas/home-assistant-automation-yaml-writable` per user request.
- [x] Documentation impact identified; `docs/runbooks/home-assistant.md` will be updated.
- [x] PR review/status checks are the review gate; this implementation will not create verifier approval or open a PR.

## Project Structure

### SDD Artifacts

```text
specs/home-assistant-automation-yaml-writable/
├── spec.md
├── plan.md
├── tasks.md
└── evidence.md
```

### Source Or Documentation Changes

```text
docs/runbooks/home-assistant.md
kubernetes/apps/home-assistant/deployment.yaml
kubernetes/apps/home-assistant/kustomization.yaml
kubernetes/apps/home-assistant/config/automations.yaml
kubernetes/apps/home-assistant/branch/home-assistant.yaml
kubernetes/apps/home-assistant/branch/kustomization.yaml
kubernetes/apps/home-assistant/branch/config/automations.yaml
specs/home-assistant-automation-yaml-writable/
```

## Tiered TDD And Validation Plan

**TDD expectation**: This is manifest behavior with no unit-test seam; use render-first and source/render assertions as focused tests.

**Local checks**:

- `kubectl kustomize kubernetes/apps/home-assistant`
- `kubectl kustomize kubernetes/apps/home-assistant/branch`
- Source/render assertions for absent `automations.yaml` ConfigMap key, absent `/config/automations.yaml` volume mount, present conditional seed command, and preserved automation include
- `python3 tools/architecture/render.py --check`
- `python3 tools/codex-harness/validate_active_implementation.py`
- `python3 tools/codex-harness/validate_implementation_plan.py --branch "$(git branch --show-current)"`
- `python3 tools/codex-harness/validate_workflow_attestations.py --kind owner`
- `python3 tools/codex-harness/validate_sdd_context.py --root "$(pwd)" --branch "$(git branch --show-current)" --require-plan-artifacts --require-evidence`
- `git diff --check`

**Development smoke**: Run Home Assistant branch smoke with `--push` using `~/.kube/homelab-development.config` after staging development smoke secrets; record the smoke-tested SHA and report path or the blocker and substitute checks.

**Automated smoke preference**: For this routed app behavior change, the Home Assistant development profile is the preferred automated smoke. If unavailable, substitute render/source checks and record the unverified live UI save layer.

**Completion evidence**: Record rendered intent, pushed/smoke-tested SHA if smoke runs, development profile result, final branch `HEAD`, and exact command outcomes.

**Fanout plan**: After edits, render checks, source assertions, architecture check, workflow validators, and documentation/evidence review are independent read-only tasks; consolidate all results in `evidence.md`.

**Evidence destination**: `specs/home-assistant-automation-yaml-writable/evidence.md`.

## Documentation Impact

Update `docs/runbooks/home-assistant.md` to state that UI-managed automations live on the PVC, must remain writable, and must not be ConfigMap-mounted.

## Implementation Steps

1. Create workflow scratch files and durable Spec Kit artifacts for `home-assistant-automation-yaml-writable`.
2. Remove the `automations.yaml` ConfigMap generator entries and read-only mounts from base and branch manifests.
3. Add conditional init-container seeding for `/config/automations.yaml` in base and branch.
4. Delete unreferenced tracked `config/automations.yaml` files.
5. Update the Home Assistant runbook with the writable automations invariant.
6. Run local render/source/workflow checks, development smoke if feasible, record evidence, and commit.

## Risks

| Risk | Mitigation |
| ---- | ---------- |
| Existing runtime automations are overwritten | Seed command uses `[ -f /config/automations.yaml ] || ...` so existing PVC files are preserved. |
| Fresh PVC starts without a valid automations include target | Init container creates `[]` before Home Assistant starts. |
| Future changes reintroduce the read-only mount | Runbook documents the invariant and validation checks assert the mount/key are absent. |
| Development smoke cannot prove the exact UI save path | Record the smoke layer proved and the remaining unverified UI save layer if browser/API credentials are unavailable. |

## Complexity Tracking

> Fill only when the constitution check has a violation that must be justified.

| Violation | Why Needed | Simpler Alternative Rejected Because |
| --------- | ---------- | ------------------------------------ |
| N/A | N/A | N/A |
