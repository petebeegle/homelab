# Feature Specification: home-assistant-elgato-lighting

**Feature Branch**: `codex/home-assistant-elgato-lighting`
**Created**: 2026-07-04
**Status**: Draft
**Risk Tier**: medium
**Input**: User description: "lets integrate elgato lighting into home assistant"

## Summary

Operators need a GitOps-owned Home Assistant automation that balances the two
desk Elgato Key Light Air fills from the observed desk illuminance while keeping
manual control over whether the automation is active. The existing Elgato
runtime onboarding guidance remains valid; this implementation adds the known
entity-ID based helper and automation after pairing.

## Binding Sources

- `AGENTS.md`
- `.specify/memory/constitution.md`
- `docs/runbooks/implementation-workflow.md`
- `docs/runbooks/spec-driven-development.md`
- `docs/runbooks/home-assistant.md`

## Scope

### In Scope

- Add a Git-owned `input_boolean.desk_light_auto_balance` helper.
- Add a Git-owned Home Assistant automation that triggers when
  `sensor.office_desk_illuminance` changes and only runs when the helper is on.
- Control `light.elgato_key_light_air_ambient` as the main/farther left-center
  fill and `light.elgato_key_light_air_camera` as the softer close/right camera
  fill.
- Apply the requested stepped brightness and kelvin settings for bright, light,
  medium, and strong fill levels.
- Keep production/base and development branch-overlay Home Assistant config
  shapes aligned.
- Update SDD planning and evidence for a medium-risk Home Assistant app
  behavior/config change.

### Out Of Scope

- Home Assistant YAML integration entries for Elgato Light; pairing remains a
  runtime config-flow concern.
- Kubernetes workload, Gateway, Secret, Flux, Service, PVC, storage, or image
  changes.
- Runtime Home Assistant `.storage`, config entries, credentials, or generated
  registries.
- Live device discovery or renaming.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Balance Desk Fill Lights Automatically (Priority: P1)

An operator can enable a helper and have Home Assistant automatically adjust both
desk Elgato fill lights whenever the office desk illuminance sensor changes.

**Why this priority**: The known entity IDs now make the useful Git-owned desk
lighting behavior possible.

**Independent Test**: Review the package YAML and confirm the helper, trigger,
condition, target lights, transition, and stepped fill levels match this spec.

**Acceptance Scenarios**:

1. **Given** `input_boolean.desk_light_auto_balance` is `off`, **When**
   `sensor.office_desk_illuminance` changes, **Then** the automation does not
   change either Elgato light.
2. **Given** the helper is `on`, **When** the illuminance changes to at least
   `400`, **Then** both Elgato lights are turned off with transition `3`.
3. **Given** the helper is `on`, **When** the illuminance changes to `250`
   through `399`, **Then** the ambient light turns on at `35%` and `4000K`, and
   the camera light turns on at `18%` and `3800K`, both with transition `3`.
4. **Given** the helper is `on`, **When** the illuminance changes to `100`
   through `249`, **Then** the ambient light turns on at `55%` and `3800K`, and
   the camera light turns on at `28%` and `3600K`, both with transition `3`.
5. **Given** the helper is `on`, **When** the illuminance changes below `100`,
   **Then** the ambient light turns on at `75%` and `3500K`, and the camera
   light turns on at `38%` and `3300K`, both with transition `3`.

## Requirements *(mandatory)*

- **FR-001**: The implementation MUST define or use
  `input_boolean.desk_light_auto_balance` as the manual enable helper.
- **FR-002**: The automation MUST trigger when
  `sensor.office_desk_illuminance` changes.
- **FR-003**: The automation MUST only run when
  `input_boolean.desk_light_auto_balance` is `on`.
- **FR-004**: The automation MUST target
  `light.elgato_key_light_air_ambient` as the main/farther left-center fill and
  `light.elgato_key_light_air_camera` as the softer close/right camera fill.
- **FR-005**: The automation MUST use transition `3` for all turn-on and
  turn-off actions.
- **FR-006**: At `>=400` lux, the automation MUST turn both Elgato lights off.
- **FR-007**: At `250-399` lux, the automation MUST set light fill: ambient
  `35%`/`4000K`, camera `18%`/`3800K`.
- **FR-008**: At `100-249` lux, the automation MUST set medium fill: ambient
  `55%`/`3800K`, camera `28%`/`3600K`.
- **FR-009**: At `<100` lux, the automation MUST set strong fill: ambient
  `75%`/`3500K`, camera `38%`/`3300K`.
- **FR-010**: Production/base and branch-overlay Home Assistant config MUST
  include the same helper and automation shape.
- **FR-011**: The implementation MUST NOT commit runtime Home Assistant
  `.storage`, config entries, device credentials, SOPS secret changes, or
  generated architecture docs.
- **FR-012**: Evidence MUST record local render checks, YAML/config sanity
  checks available without live Home Assistant, workflow validators, and any
  development validation exception.

## Risk And Validation Expectations

**Medium**: This changes Git-owned Home Assistant app behavior/config and the
branch overlay. Run production and branch kustomize renders, static YAML/config
sanity checks available without live Home Assistant, workflow validators, and
development validation or a documented unavailable-infrastructure exception with
substitute checks.

## Success Criteria *(mandatory)*

- **SC-001**: `kubernetes/apps/home-assistant/config/packages/code_first.yaml`
  defines the helper and automation with the required trigger, condition,
  targets, thresholds, brightness percentages, kelvin values, and transitions.
- **SC-002**:
  `kubernetes/apps/home-assistant/branch/config/packages/code_first.yaml`
  matches the production/base package behavior.
- **SC-003**: `kubectl kustomize kubernetes/apps/home-assistant` passes.
- **SC-004**: `kubectl kustomize kubernetes/apps/home-assistant/branch` passes.
- **SC-005**: A YAML/config sanity check confirms the package files parse as
  ordinary YAML with the expected top-level Home Assistant package domains.
- **SC-006**: SDD and workflow validation passes for the implementation owner
  context.

## Assumptions

- The named illuminance sensor and Elgato light entities already exist in
  runtime Home Assistant.
- The Home Assistant package include remains enabled through
  `homeassistant: packages: !include_dir_named packages`.
- The helper defaults to off until an operator enables it in Home Assistant.

## Open Questions

- None
