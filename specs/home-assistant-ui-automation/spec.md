# Feature Specification: home-assistant-ui-automation

**Feature Branch**: `codex/home-assistant-ui-automation`
**Created**: 2026-07-04
**Status**: Draft
**Risk Tier**: medium
**Input**: User description: "user migrated the Desk Elgato Ambient Balance automation to the Home Assistant UI and wants the Git-owned version deleted from code"

## Summary

Operators need Git to stop owning the desk Elgato ambient-balance helper and
automation because the behavior now lives in Home Assistant UI-managed runtime
state. The repository should preserve only the minimal package structure and
document that Git must not recreate those entities unless intentionally moving
the behavior back to code.

## Binding Sources

- `AGENTS.md`
- `.specify/memory/constitution.md`
- `docs/runbooks/implementation-workflow.md`
- `docs/runbooks/spec-driven-development.md`
- `docs/runbooks/home-assistant.md`

## Scope

### In Scope

- Remove `input_boolean.desk_light_auto_balance` from the Git-owned Home
  Assistant base package.
- Remove the Git-owned automation with id `desk_elgato_ambient_balance` from
  the Home Assistant base package.
- Mirror the removal in the Home Assistant branch overlay package.
- Keep both package files valid YAML with the existing minimal
  `homeassistant: customize: {}` package structure.
- Update Home Assistant runbook guidance to state that the desk Elgato balance
  automation is UI-managed runtime state.
- Record Spec Kit artifacts and evidence for a medium Home Assistant app config
  behavior change.

### Out Of Scope

- Runtime Home Assistant `.storage`, generated registries, config entries, or
  UI state changes.
- Kubernetes workload, Gateway, PVC, Service, Flux, secret, storage class, image,
  or generated architecture documentation changes.
- Verifier approval creation, branch push, or PR creation.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Git Stops Owning UI-Managed Desk Balance (Priority: P1)

An operator can keep managing the desk Elgato ambient-balance behavior in the
Home Assistant UI without Flux reintroducing the old Git-owned helper or
automation.

**Why this priority**: It is the smallest useful slice that resolves the
ownership conflict after migration to the UI.

**Independent Test**: Search Git-owned Home Assistant config and confirm
`desk_elgato_ambient_balance` and `desk_light_auto_balance` no longer appear in
package/config files while the package YAML still renders through kustomize.

**Acceptance Scenarios**:

1. **Given** the Home Assistant package files are rendered from Git, **When**
   Flux applies the base or branch overlay ConfigMap, **Then** Git does not
   define `input_boolean.desk_light_auto_balance` or automation id
   `desk_elgato_ambient_balance`.
2. **Given** an operator reviews the Home Assistant runbook, **When** they look
   for desk Elgato balance ownership, **Then** the runbook states the behavior
   is UI-managed runtime state and should not be re-added to Git unless moving
   it back to code intentionally.

## Requirements *(mandatory)*

- **FR-001**: The implementation MUST remove
  `input_boolean.desk_light_auto_balance` from
  `kubernetes/apps/home-assistant/config/packages/code_first.yaml`.
- **FR-002**: The implementation MUST remove automation id
  `desk_elgato_ambient_balance` from
  `kubernetes/apps/home-assistant/config/packages/code_first.yaml`.
- **FR-003**: The implementation MUST mirror the helper and automation removal
  in `kubernetes/apps/home-assistant/branch/config/packages/code_first.yaml`.
- **FR-004**: The package files MUST remain valid YAML and keep the existing
  minimal `homeassistant: customize: {}` structure when no other package content
  remains.
- **FR-005**: The Home Assistant runbook MUST document that the desk Elgato
  balance automation is UI-managed/runtime state and Git should not re-add the
  helper or automation unless intentionally moving it back to code.
- **FR-006**: The implementation MUST NOT edit runtime `.storage`, secrets,
  Kubernetes workload/Gateway/PVC/Service/Flux wiring, or generated architecture
  docs.
- **FR-007**: Evidence MUST record base and branch kustomize renders, package
  parity diff, removed-identifier search, workflow validators,
  `git diff --check`, `git status --short`, and development smoke outcome or
  exception.

## Risk And Validation Expectations

**Medium**: This changes Git-owned Home Assistant app config behavior and the
branch overlay. Run focused kustomize renders, package parity diff, static
removed-identifier search, workflow validators, and development validation when
feasible. If the development branch smoke is unavailable or inappropriate before
push, record an exception and substitute local checks.

## Success Criteria *(mandatory)*

- **SC-001**: Both `code_first.yaml` package files contain only the minimal
  Home Assistant package structure after the helper and automation are removed.
- **SC-002**: `kubectl kustomize kubernetes/apps/home-assistant` passes.
- **SC-003**: `kubectl kustomize kubernetes/apps/home-assistant/branch` passes.
- **SC-004**: A package parity diff shows no base/branch package drift.
- **SC-005**: Search confirms the removed identifiers are absent from Git-owned
  Home Assistant config.
- **SC-006**: Workflow validators pass for the marker, implementation plan,
  owner attestation, delegation token evidence, and SDD context.

## Assumptions

- The user has already migrated the automation and any required helper/runtime
  state through the Home Assistant UI.
- Existing runtime UI state on the Home Assistant PVC will continue to own the
  behavior after Git stops defining these entities.
- No generated architecture update is required because Kubernetes/Terraform
  wiring is unchanged.

## Open Questions

- None
