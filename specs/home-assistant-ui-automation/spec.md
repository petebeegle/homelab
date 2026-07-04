# Feature Specification: home-assistant-ui-automation

**Feature Branch**: `codex/home-assistant-ui-automation`
**Created**: 2026-07-04
**Status**: Draft
**Risk Tier**: medium
**Input**: User description: "user migrated the Desk Elgato Ambient Balance automation to the Home Assistant UI and wants the Git-owned version deleted from code; follow-up production bug found because Home Assistant cannot atomically replace ConfigMap-mounted `/config/automations.yaml`"

## Summary

Operators need Git to stop owning the desk Elgato ambient-balance helper and
automation because the behavior now lives in Home Assistant UI-managed runtime
state. Home Assistant must also be able to save UI-managed automations by
atomically replacing `/config/automations.yaml`, which requires that file to
live on the writable PVC instead of being mounted read-only from a ConfigMap.

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
- Stop mounting `/config/automations.yaml` from a ConfigMap in production/base
  and branch Home Assistant workloads.
- Remove the no-longer-referenced Git-owned base and branch `automations.yaml`
  files from configMap generators and tracked files.
- Seed `/config/automations.yaml` with `[]` on the writable PVC at startup when
  the file is missing.
- Record Spec Kit artifacts and evidence for a medium Home Assistant app config
  behavior change.

### Out Of Scope

- Runtime Home Assistant `.storage`, generated registries, config entries, or
  UI state changes.
- Gateway, PVC, Service, Flux, secret, storage class, image, script, scene,
  OIDC, runtime `.storage`, or generated architecture documentation changes.
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

### User Story 2 - UI Automations Save To Writable PVC (Priority: P1)

An operator can save Home Assistant UI automations because
`/config/automations.yaml` is no longer a read-only ConfigMap subPath mount and
exists on the writable PVC for fresh deployments.

**Why this priority**: This fixes the production 500 error when Home Assistant
tries to atomically replace `automations.yaml`.

**Independent Test**: Render the base and branch manifests and confirm
`/config/automations.yaml` is not mounted from the ConfigMap, the ConfigMap does
not include `automations.yaml`, and the init container seeds `[]` when the file
is missing.

**Acceptance Scenarios**:

1. **Given** a fresh Home Assistant PVC without `automations.yaml`, **When** the
   pod starts, **Then** the init container creates `/config/automations.yaml`
   with `[]`.
2. **Given** Home Assistant saves UI automations, **When** it writes a temporary
   file and renames it to `/config/automations.yaml`, **Then** the target path
   is PVC-backed and writable rather than a read-only ConfigMap mount.
3. **Given** existing UI-managed automations already exist on the PVC, **When**
   the pod restarts, **Then** the init container does not overwrite the existing
   file.

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
- **FR-007**: Production/base and branch Home Assistant workloads MUST NOT mount
  `/config/automations.yaml` from a ConfigMap or other read-only source.
- **FR-008**: Production/base and branch Home Assistant ConfigMap generators
  MUST NOT include `automations.yaml=config/automations.yaml`.
- **FR-009**: Git-owned base and branch `config/automations.yaml` files MUST be
  removed when they are no longer referenced.
- **FR-010**: Production/base and branch init containers MUST create
  `/config/automations.yaml` with valid empty automation list content (`[]`)
  only when the file is missing.
- **FR-011**: `configuration.yaml` MUST continue to use
  `automation: !include automations.yaml`.
- **FR-012**: The Home Assistant runbook MUST document that UI-managed
  automations require `/config/automations.yaml` to remain PVC-writable and not
  ConfigMap-mounted.
- **FR-013**: Evidence MUST record base and branch kustomize renders, package
  parity diff, removed-identifier search, workflow validators,
  automation mount/content checks, architecture render check, `git diff
  --check`, `git status --short`, and development smoke outcome or exception.

## Risk And Validation Expectations

**Medium**: This changes Git-owned Home Assistant app config behavior,
Kubernetes workload mounts/init behavior, and the branch overlay. Run focused
kustomize renders, package parity diff, static removed-identifier and mount
checks, workflow validators, architecture render check, and development
validation when feasible.

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
- **SC-007**: Render/content checks confirm `automations.yaml` is absent from
  ConfigMap-generated data and no longer mounted at `/config/automations.yaml`.
- **SC-008**: Render/content checks confirm the init containers seed
  `/config/automations.yaml` with `[]` only when missing.
- **SC-009**: Development smoke passes for the Home Assistant branch profile.

## Assumptions

- The user has already migrated the automation and any required helper/runtime
  state through the Home Assistant UI.
- Existing runtime UI state on the Home Assistant PVC will continue to own the
  behavior after Git stops defining these entities.
- Existing runtime `/config/automations.yaml` should not be overwritten on pod
  restart.
- No generated architecture update is required because Kubernetes/Terraform
  wiring is unchanged.

## Open Questions

- None
