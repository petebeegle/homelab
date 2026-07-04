# Implementation Plan: home-assistant-ui-automation

**Branch**: `codex/home-assistant-ui-automation` | **Date**: 2026-07-04 | **Spec**:
`specs/home-assistant-ui-automation/spec.md`

**Input**: Feature specification from
`specs/home-assistant-ui-automation/spec.md`

## Summary

Remove the Git-owned Home Assistant helper and automation for the desk Elgato
ambient-balance behavior now that the user has migrated the behavior to the Home
Assistant UI. Also make `/config/automations.yaml` PVC-backed and writable by
removing its ConfigMap generator entry and read-only subPath mount, while
seeding `[]` on fresh PVCs so Home Assistant can save UI-managed automations.

## Technical Context

**Risk Tier**: medium
**Workflow Tier**: medium
**Primary Areas**: Home Assistant package YAML, workload mounts/init commands,
branch overlay, Home Assistant runbook, SDD artifacts
**Dependencies**: Existing Home Assistant package include and kustomize render
tooling
**Storage**: Existing Home Assistant PVC remains unchanged; UI-managed runtime
state stays under `/config/.storage`, and UI-managed `automations.yaml` stays
on the writable `/config` PVC
**Ingress**: No Gateway API route changes
**Secrets**: No SOPS changes
**Development Validation**: Home Assistant branch smoke with the development
kubeconfig and `--push` when feasible

## Constitution Check

*GATE: Must pass before tracked edits and be re-checked before commit.*

- [x] GitOps source of truth preserved for declarative config; Git stops
      declaring UI-managed helper/automation and leaves runtime automation YAML
      state on the PVC.
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
kubernetes/apps/home-assistant/deployment.yaml
kubernetes/apps/home-assistant/branch/home-assistant.yaml
kubernetes/apps/home-assistant/kustomization.yaml
kubernetes/apps/home-assistant/branch/kustomization.yaml
kubernetes/apps/home-assistant/config/automations.yaml
kubernetes/apps/home-assistant/branch/config/automations.yaml
docs/runbooks/home-assistant.md
specs/home-assistant-ui-automation/
```

## Tiered TDD And Validation Plan

**TDD expectation**: Medium-risk configuration/workload behavior with no local
Home Assistant runtime unit-test seam. Use kustomize renders, package parity
diff, removed-identifier search, rendered mount/content checks, architecture
render check, workflow validators, and development smoke.

**Local checks**:

- `kubectl kustomize kubernetes/apps/home-assistant`
- `kubectl kustomize kubernetes/apps/home-assistant/branch`
- `diff -u kubernetes/apps/home-assistant/config/packages/code_first.yaml kubernetes/apps/home-assistant/branch/config/packages/code_first.yaml`
- `rg 'desk_elgato_ambient_balance|desk_light_auto_balance' kubernetes/apps/home-assistant`
- Render/content checks confirming `automations.yaml` is not ConfigMap-mounted
  and init containers seed it on the PVC when missing.
- `python3 tools/architecture/render.py --check`
- `python3 tools/codex-harness/validate_active_implementation.py --root "$(pwd)" --branch "$(git branch --show-current)"`
- `python3 tools/codex-harness/validate_implementation_plan.py --root "$(pwd)" --branch "$(git branch --show-current)"`
- `python3 tools/codex-harness/validate_workflow_attestations.py --kind owner --root "$(pwd)" --branch "$(git branch --show-current)"`
- `python3 tools/codex-harness/validate_sdd_context.py --root "$(pwd)" --branch "$(git branch --show-current)" --require-plan-artifacts --require-evidence`
- `git diff --check`
- `git status --short`

**Development smoke**: Run
`python3 tools/development/verify_branch_deploy.py --app home-assistant --branch codex/home-assistant-ui-automation --slug home-assistant-ui-automation --kubeconfig ~/.kube/homelab-development.config --timeout 20m --push`
when feasible, then record pushed SHA, runtime checks, and cleanup.

**Evidence destination**: `specs/home-assistant-ui-automation/evidence.md`.

## Documentation Impact

Update `docs/runbooks/home-assistant.md` to state that the desk Elgato
ambient-balance automation is now UI-managed runtime state and Git should not
re-add the helper/automation unless intentionally moving it back to code. Also
document that UI-managed automations require `/config/automations.yaml` to
remain PVC-writable and not ConfigMap-mounted. Run the generated architecture
check because Kubernetes manifests change.

## Implementation Steps

1. Create workflow marker, implementation plan, owner attestation, delegation
   token evidence, and SDD artifacts.
2. Remove the desk helper and automation from the base Home Assistant
   `code_first.yaml` package while preserving minimal package YAML.
3. Mirror the removal in the branch overlay `code_first.yaml` package.
4. Update the Home Assistant runbook ownership note.
5. Remove the ConfigMap generator entries and read-only mounts for
   `automations.yaml` in production/base and branch manifests.
6. Seed `/config/automations.yaml` with `[]` from the existing init containers
   when missing, without overwriting existing PVC content.
7. Run local renders, parity diff, removed-identifier search, mount/content
   checks, architecture check, workflow validators, diff/status checks, and
   development smoke.
8. Record command outcomes and final branch state in evidence.
9. Amend the existing conventional commit.

## Risks

| Risk | Mitigation |
| ---- | ---------- |
| Git reintroduces a runtime-owned helper or automation later | Add concise runbook guidance that the behavior is UI-managed unless intentionally moved back to code |
| Empty package YAML becomes invalid or changes include behavior | Preserve `homeassistant: customize: {}` in both package files |
| Home Assistant still cannot save UI automations | Remove the read-only subPath mount and keep the file on the writable PVC |
| Fresh PVC lacks `automations.yaml` | Seed `[]` from the init container only when missing |
| Init seeding overwrites existing runtime automations | Use `[ -f /config/automations.yaml ] || ...` so existing files are preserved |

## Complexity Tracking

> Fill only when the constitution check has a violation that must be justified.

| Violation | Why Needed | Simpler Alternative Rejected Because |
| --------- | ---------- | ------------------------------------ |
| N/A | N/A | N/A |
