# Implementation Plan: home-assistant-elgato-lighting

**Branch**: `codex/home-assistant-elgato-lighting` | **Date**: 2026-07-04 | **Spec**:
`specs/home-assistant-elgato-lighting/spec.md`

**Input**: Feature specification from
`specs/home-assistant-elgato-lighting/spec.md`

## Summary

Add the GitOps-owned Home Assistant helper and automation for the desk Elgato
ambient-balance behavior now that the required runtime entity IDs are known. The
automation lives in the existing `code_first.yaml` package so the helper and
automation are managed together in production/base and the branch overlay.

## Technical Context

**Risk Tier**: medium
**Workflow Tier**: medium
**Primary Areas**: Home Assistant package YAML, branch overlay, SDD artifacts,
Home Assistant runbook note
**Dependencies**: Existing Home Assistant package include, known Elgato and
illuminance entity IDs
**Storage**: Existing Home Assistant PVC remains unchanged; runtime integration
state stays under `/config/.storage`
**Ingress**: No Gateway API route changes
**Secrets**: No SOPS changes
**Development Validation**: required for medium-risk app behavior when
infrastructure is available; otherwise record an unavailable-infrastructure
exception and substitute local render/static checks

## Constitution Check

*GATE: Must pass before tracked edits and be re-checked before commit.*

- [x] GitOps source of truth preserved; no durable live-cluster-only state.
- [x] No production-first mutation; development validation plan or exception is
      recorded for covered changes.
- [x] Gateway API invariant preserved; no new Kubernetes `Ingress` resources.
- [x] SOPS invariant preserved; no plaintext secret manifests staged.
- [x] NFS default considered for PVC-backed workloads.
- [x] Talos boundary preserved; no SSH-based node operations introduced.
- [x] Branch is `codex/home-assistant-elgato-lighting`; worktree/current-checkout mode is
      intentional and recorded when relevant.
- [x] Documentation impact identified; docs updated or no-docs rationale
      recorded.
- [x] PR review/status checks are the review gate.

## Project Structure

### SDD Artifacts

```text
specs/home-assistant-elgato-lighting/
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
specs/home-assistant-elgato-lighting/
```

## Tiered TDD And Validation Plan

**TDD expectation**: Medium-risk configuration behavior. There is no local Home
Assistant runtime test seam in this repo, so use static package review,
production and branch kustomize renders, and a YAML/config sanity check as the
local red/green substitute. Record any unavailable live Home Assistant
validation exception.

**Local checks**:

- `kubectl kustomize kubernetes/apps/home-assistant`
- `kubectl kustomize kubernetes/apps/home-assistant/branch`
- YAML/config sanity check for the edited package files
- Workflow harness validators
- `git status --short`

**Development smoke**: Home Assistant app behavior validation is expected for
medium risk when a development cluster and matching runtime entities are
available. If unavailable, document the exception, include substitute local
checks, and leave verifier review to decide whether more smoke is required.

**Evidence destination**: `specs/home-assistant-elgato-lighting/evidence.md`.

## Documentation Impact

Keep `docs/runbooks/home-assistant.md` current by noting that the desk Elgato
ambient-balance automation is now Git-owned in `code_first.yaml`. No generated
architecture update is required because Kubernetes and Terraform sources do not
change shape beyond ConfigMap input content.

## Implementation Steps

1. Revise SDD artifacts and local implementation plan from docs-only to
   medium-risk Home Assistant app behavior/config.
2. Add `input_boolean.desk_light_auto_balance` and the desk Elgato
   ambient-balance automation to production/base `code_first.yaml`.
3. Mirror the helper and automation in the branch-overlay `code_first.yaml`.
4. Update the Home Assistant runbook only as needed to mention the Git-owned
   automation.
5. Run local render, YAML/config sanity, workflow, and status checks.
6. Record command outcomes, development validation evidence or exception, and
   final branch state in evidence.

## Risks

| Risk | Mitigation |
| ---- | ---------- |
| Helper defaults unexpectedly active | Define a normal `input_boolean`; Home Assistant defaults it off unless restored runtime state says otherwise |
| Automation targets missing or renamed entities | Use the exact entity IDs from the user plan and require live HA validation or record the unavailable-infrastructure exception |
| Package YAML syntax is invalid | Run static YAML/config sanity checks plus production and branch kustomize renders |

## Complexity Tracking

> Fill only when the constitution check has a violation that must be justified.

| Violation | Why Needed | Simpler Alternative Rejected Because |
| --------- | ---------- | ------------------------------------ |
| N/A | N/A | N/A |
