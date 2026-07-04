# Feature Specification: home-assistant-elgato-lighting

**Feature Branch**: `codex/home-assistant-elgato-lighting`
**Created**: 2026-07-04
**Status**: Draft
**Risk Tier**: tiny
**Input**: User description: "lets integrate elgato lighting into home assistant"

## Summary

Operators need clear, GitOps-safe instructions for pairing Elgato lighting with
Home Assistant. The first useful slice documents runtime onboarding and the
boundary between Home Assistant config-flow state and code-owned controls, so no
fake integration YAML, device credentials, or guessed entity IDs are committed.

## Binding Sources

- `AGENTS.md`
- `.specify/memory/constitution.md`
- `docs/runbooks/implementation-workflow.md`
- `docs/runbooks/spec-driven-development.md`
- `docs/runbooks/home-assistant.md`

## Scope

### In Scope

- Document Elgato Light discovery and manual host setup through the Home
  Assistant UI.
- Document runtime inventory capture after pairing.
- Document that Elgato runtime state remains on the Home Assistant PVC under
  `/config/.storage` and must not be committed.
- Record SDD planning and evidence for the docs-only implementation.

### Out Of Scope

- Home Assistant YAML integration entries for Elgato Light.
- Kubernetes workload, Gateway, Secret, Flux, Service, PVC, or storage changes.
- Git-owned scenes, scripts, automations, or package controls before real
  Elgato entity IDs are known.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Pair Elgato Lights Safely (Priority: P1)

An operator can onboard Elgato lights in Home Assistant while preserving the
repo boundary between GitOps-owned YAML and runtime Home Assistant state.

**Why this priority**: Pairing creates the entity IDs needed before any useful
code-owned lighting control can be added.

**Independent Test**: Review `docs/runbooks/home-assistant.md` and confirm it
documents discovery, manual host setup, runtime inventory capture, and
`.storage` safety.

**Acceptance Scenarios**:

1. **Given** an Elgato light on the same reachable LAN as Home Assistant,
   **When** the operator opens Home Assistant Devices & services, **Then** the
   runbook explains accepting a discovered Elgato Light integration or adding it
   manually by hostname or IP.
2. **Given** an Elgato light is paired, **When** the operator prepares a
   follow-up GitOps change, **Then** the runbook says to record real entity IDs
   and supported features before adding scenes, scripts, automations, or package
   YAML.

## Requirements *(mandatory)*

- **FR-001**: The implementation MUST document Elgato Light setup through Home
  Assistant Devices & services.
- **FR-002**: The implementation MUST document manual setup by hostname or IP
  when zeroconf discovery does not find a light.
- **FR-003**: The implementation MUST document the expected generated entities:
  the main `light.*` entity and optional identify/restart buttons, battery
  sensor, or studio-mode switch depending on model.
- **FR-004**: The implementation MUST preserve the Home Assistant runtime-state
  boundary by warning against committing `/config/.storage`, `config_entries`,
  device credentials, or generated registry files.
- **FR-005**: The implementation MUST NOT change Kubernetes manifests, Home
  Assistant integration YAML, SOPS secrets, or generated architecture docs.
- **FR-006**: Evidence MUST record local render checks and the docs-only
  development-smoke exception.

## Risk And Validation Expectations

**Tiny**: This is a docs-only implementation. Run cheap render checks for the
existing Home Assistant production and branch kustomizations and perform a
focused runbook review.

## Success Criteria *(mandatory)*

- **SC-001**: `docs/runbooks/home-assistant.md` contains Elgato-specific
  pairing, manual setup, inventory, and runtime-state safety guidance.
- **SC-002**: `kubectl kustomize kubernetes/apps/home-assistant` passes.
- **SC-003**: `kubectl kustomize kubernetes/apps/home-assistant/branch` passes.
- **SC-004**: `git diff --name-only` shows only the Home Assistant runbook and
  `specs/home-assistant-elgato-lighting/` files.

## Assumptions

- No Elgato device IPs, hostnames, or Home Assistant entity IDs are known yet.
- The first useful repo change is operator guidance, not automation.
- A later implementation can add Git-owned studio scenes or scripts once real
  entity IDs are captured from Home Assistant.

## Open Questions

- None
