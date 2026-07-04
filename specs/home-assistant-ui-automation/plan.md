# Implementation Plan: home-assistant-ui-automation

**Branch**: `codex/home-assistant-ui-automation` | **Date**: 2026-07-04 | **Spec**:
`specs/home-assistant-ui-automation/spec.md`

**Input**: Feature specification from
`specs/home-assistant-ui-automation/spec.md`

## Summary

Remove the Git-owned Home Assistant helper and automation for the desk Elgato
ambient-balance behavior now that the user has migrated the behavior to the Home
Assistant UI. Preserve the minimal package shape in both base and branch overlay
files and update the runbook so future Git changes do not accidentally reclaim
runtime-owned UI state.

## Technical Context

**Risk Tier**: medium
**Workflow Tier**: medium
**Primary Areas**: Home Assistant package YAML, branch overlay, Home Assistant
runbook, SDD artifacts
**Dependencies**: Existing Home Assistant package include and kustomize render
tooling
**Storage**: Existing Home Assistant PVC remains unchanged; UI-managed runtime
state stays under `/config/.storage`
**Ingress**: No Gateway API route changes
**Secrets**: No SOPS changes
**Development Validation**: manual Home Assistant branch smoke if feasible with
existing development kubeconfig and branch workflow; otherwise record an
unavailable/inappropriate-before-push exception with substitute local render and
static checks

## Constitution Check

*GATE: Must pass before tracked edits and be re-checked before commit.*

- [x] GitOps source of truth preserved; Git stops declaring the UI-managed
      helper/automation and leaves runtime UI state on the PVC.
- [x] No production-first mutation; development validation plan or exception is
      recorded for covered changes.
- [x] Gateway API invariant preserved; no new Kubernetes `Ingress` resources.
- [x] SOPS invariant preserved; no plaintext secret manifests staged.
- [x] NFS default considered for PVC-backed workloads; no PVC/storage changes.
- [x] Talos boundary preserved; no SSH-based node operations introduced.
- [x] Branch is `codex/home-assistant-ui-automation`; sibling clone/current
      checkout path is `/workspaces/homelab-ideas/home-assistant-ui-automation`.
- [x] Documentation impact identified; `docs/runbooks/home-assistant.md` will
      be updated.
- [x] PR review/status checks are the review gate.

## Project Structure

### SDD Artifacts

```text
specs/home-assistant-ui-automation/
├── spec.md
├── plan.md
├── tasks.md
└── evidence.md
```

### Source Or Documentation Changes

```text
kubernetes/apps/home-assistant/config/packages/code_first.yaml
kubernetes/apps/home-assistant/branch/config/packages/code_first.yaml
docs/runbooks/home-assistant.md
specs/home-assistant-ui-automation/
```

## Tiered TDD And Validation Plan

**TDD expectation**: Medium-risk configuration behavior with no local Home
Assistant runtime unit-test seam. Use kustomize renders, package parity diff,
removed-identifier search, and workflow validators as local substitutes.

**Local checks**:

- `kubectl kustomize kubernetes/apps/home-assistant`
- `kubectl kustomize kubernetes/apps/home-assistant/branch`
- `diff -u kubernetes/apps/home-assistant/config/packages/code_first.yaml kubernetes/apps/home-assistant/branch/config/packages/code_first.yaml`
- `rg 'desk_elgato_ambient_balance|desk_light_auto_balance' kubernetes/apps/home-assistant`
- `python3 tools/codex-harness/validate_active_implementation.py --root "$(pwd)" --branch "$(git branch --show-current)"`
- `python3 tools/codex-harness/validate_implementation_plan.py --root "$(pwd)" --branch "$(git branch --show-current)"`
- `python3 tools/codex-harness/validate_workflow_attestations.py --kind owner --root "$(pwd)" --branch "$(git branch --show-current)"`
- `python3 tools/codex-harness/validate_sdd_context.py --root "$(pwd)" --branch "$(git branch --show-current)" --require-plan-artifacts --require-evidence`
- `git diff --check`
- `git status --short`

**Development smoke**: Run if feasible with existing development kubeconfig and
branch workflow. Because the user instructed not to push and branch smoke
automation normally requires pushing branch manifests, record an exception if no
safe no-push smoke path is available and rely on substitute local checks.

**Evidence destination**: `specs/home-assistant-ui-automation/evidence.md`.

## Documentation Impact

Update `docs/runbooks/home-assistant.md` to state that the desk Elgato
ambient-balance automation is now UI-managed runtime state and Git should not
re-add the helper/automation unless intentionally moving it back to code. No
generated architecture update is required because Kubernetes and Terraform
source topology is unchanged.

## Implementation Steps

1. Create workflow marker, implementation plan, owner attestation, delegation
   token evidence, and SDD artifacts.
2. Remove the desk helper and automation from the base Home Assistant
   `code_first.yaml` package while preserving minimal package YAML.
3. Mirror the removal in the branch overlay `code_first.yaml` package.
4. Update the Home Assistant runbook ownership note.
5. Run local renders, parity diff, removed-identifier search, workflow
   validators, diff/status checks, and development smoke or exception.
6. Record command outcomes and final branch state in evidence.
7. Commit with a conventional commit message and do not push.

## Risks

| Risk | Mitigation |
| ---- | ---------- |
| Git reintroduces a runtime-owned helper or automation later | Add concise runbook guidance that the behavior is UI-managed unless intentionally moved back to code |
| Empty package YAML becomes invalid or changes include behavior | Preserve `homeassistant: customize: {}` in both package files |
| Development smoke cannot be completed without pushing branch state | Record the no-push exception and include kustomize renders, parity diff, and static searches as substitutes |

## Complexity Tracking

> Fill only when the constitution check has a violation that must be justified.

| Violation | Why Needed | Simpler Alternative Rejected Because |
| --------- | ---------- | ------------------------------------ |
| N/A | N/A | N/A |
