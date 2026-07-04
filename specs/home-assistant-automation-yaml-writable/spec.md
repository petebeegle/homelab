# Feature Specification: home-assistant-automation-yaml-writable

**Feature Branch**: `codex/home-assistant-automation-yaml-writable`
**Created**: 2026-07-04
**Status**: Draft
**Risk Tier**: medium
**Input**: User issue: Home Assistant UI returns 500 when saving automations because `/config/automations.yaml` is mounted read-only from a ConfigMap with `subPath`; make it UI-writable on the PVC while preserving `automation: !include automations.yaml`.

## Summary

Home Assistant operators can save automations from the UI without a 500 error because `/config/automations.yaml` remains a writable file on the Home Assistant config PVC. Fresh PVCs still start with a valid empty automations file, and Home Assistant continues to load automations through `automation: !include automations.yaml`.

## Binding Sources

- `AGENTS.md`
- `.specify/memory/constitution.md`
- `docs/runbooks/spec-driven-development.md`
- `docs/runbooks/implementation-workflow.md`
- `docs/runbooks/home-assistant.md`
- `docs/decisions/flux-gitops-source-of-truth.md`
- `docs/decisions/synology-nfs-storage.md`
- `docs/decisions/tdd-and-development-smoke-evidence.md`

## Scope

### In Scope

- Remove the read-only `/config/automations.yaml` ConfigMap mount from base and branch Home Assistant deployments.
- Remove `automations.yaml` from the base and branch Home Assistant ConfigMap generators.
- Delete tracked base and branch `config/automations.yaml` files once they are no longer referenced.
- Seed `/config/automations.yaml` as `[]` from the init container only when the PVC file is missing.
- Preserve `automation: !include automations.yaml` in base and branch Home Assistant configuration.
- Document that UI-managed automations require the PVC-backed file to stay writable.

### Out Of Scope

- Runtime `.storage` state.
- Secrets, OIDC, Gateway, Service, PVC, scripts, scenes, packages, and generated architecture source changes unless required by validation.
- Verifier approval and PR creation.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Save UI Automations (Priority: P1)

An operator editing automations in the Home Assistant UI can save changes because Home Assistant can atomically replace `/config/automations.yaml` on the writable PVC.

**Why this priority**: This directly resolves the production 500 error and is the smallest useful behavior change.

**Independent Test**: Render base and branch manifests and confirm no Deployment mounts `/config/automations.yaml` from a ConfigMap and no generated ConfigMap includes an `automations.yaml` key.

**Acceptance Scenarios**:

1. **Given** Home Assistant runs with `/config` backed by the `home-assistant-config` PVC, **When** the UI saves automations, **Then** `/config/automations.yaml` is a writable PVC file that Home Assistant can replace.
2. **Given** a fresh Home Assistant PVC without `/config/automations.yaml`, **When** the pod init container runs, **Then** it writes `[]` to `/config/automations.yaml` before Home Assistant starts.

### User Story 2 - Preserve Existing Automation Loading (Priority: P2)

Home Assistant continues loading automations from `automations.yaml` through the existing include in `configuration.yaml`.

**Why this priority**: Making the file writable must not break Home Assistant startup or automation discovery.

**Independent Test**: Inspect base and branch `configuration.yaml` and rendered config data to confirm `automation: !include automations.yaml` remains present.

**Acceptance Scenarios**:

1. **Given** Home Assistant starts after this change, **When** it parses `configuration.yaml`, **Then** it still resolves automations from `automations.yaml`.

## Requirements *(mandatory)*

- **FR-001**: The implementation MUST remove the `/config/automations.yaml` read-only volume mount from base and branch Home Assistant Deployments.
- **FR-002**: The implementation MUST remove `automations.yaml=config/automations.yaml` from base and branch Home Assistant `configMapGenerator` entries.
- **FR-003**: The implementation MUST delete tracked base and branch `config/automations.yaml` files if no source or render path references them.
- **FR-004**: The implementation MUST seed `/config/automations.yaml` with `[]` only when it is missing from the PVC.
- **FR-005**: The implementation MUST preserve `automation: !include automations.yaml` in base and branch `configuration.yaml`.
- **FR-006**: The implementation MUST update Home Assistant runbook guidance so future changes do not reintroduce a ConfigMap or read-only mount for UI-managed automations.
- **FR-007**: Evidence MUST include base and branch kustomize renders, source/render checks for the removed mount and ConfigMap key, init seed checks, include preservation checks, workflow validators, architecture render check, `git diff --check`, and development smoke or a documented exception.

## Risk And Validation Expectations

Medium risk applies because this changes Kubernetes manifests and Home Assistant app behavior. Evidence must include focused render checks plus development-cluster validation when feasible, or a documented unavailable-infrastructure exception with substitute checks.

## Success Criteria *(mandatory)*

- **SC-001**: Base and branch renders include no `/config/automations.yaml` volume mount.
- **SC-002**: Base and branch renders include no ConfigMap data key named `automations.yaml`.
- **SC-003**: Base and branch deployments include an init-container command that creates `/config/automations.yaml` as `[]` only when missing.
- **SC-004**: Base and branch `configuration.yaml` files still contain `automation: !include automations.yaml`.
- **SC-005**: Development smoke for the Home Assistant branch profile passes with `--push`, or evidence records the blocker and substitute checks.

## Assumptions

- Existing production PVC content should be preserved; the seed command must not overwrite an existing `automations.yaml`.
- The Home Assistant UI, not Git, owns the runtime contents of `automations.yaml` after this change.
- Git-owned scripts, scenes, packages, onboarding storage seed, secrets, OIDC, Service, Gateway, and PVC behavior remain unchanged.

## Open Questions

- None.
