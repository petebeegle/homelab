# Feature Specification: home-assistant-hue-v2

**Feature Branch**: `codex/home-assistant-hue-v2`
**Created**: 2026-07-03
**Status**: Draft
**Risk Tier**: tiny
**Input**: User description: "Add Philips Hue V2 To Home Assistant"

## Summary

Document the Philips Hue V2 onboarding boundary for Home Assistant: bridge pairing is a Home Assistant UI config-flow handshake stored on the runtime PVC, while Git-owned packages, automations, scripts, and scenes come later after stable Hue entity IDs are known.

## Binding Sources

- `AGENTS.md`
- `.specify/memory/constitution.md`
- `docs/runbooks/implementation-workflow.md`
- `docs/runbooks/spec-driven-development.md`
- `docs/decisions/codex-implementation-workflow.md`
- `docs/decisions/flux-gitops-source-of-truth.md`
- `docs/decisions/sops-age-secrets.md`
- `docs/decisions/tdd-and-development-smoke-evidence.md`
- `docs/runbooks/home-assistant.md`

## Scope

### In Scope

- Add durable SDD artifacts for the Hue V2 Home Assistant onboarding milestone.
- Update the Home Assistant runbook with explicit Hue V2 pairing, inventory, and follow-up guidance.
- Record validation evidence proving the change is docs-only and does not add Hue runtime credentials or `.storage` config.

### Out Of Scope

- Pairing a physical Hue bridge.
- Editing Home Assistant PVC runtime state.
- Committing Hue `.storage` entries, config entries, bridge credentials, tokens, or fake integration YAML.
- Adding a placeholder `hue.yaml` package before entity IDs exist.
- Creating verifier approval, pushing the branch, or opening a pull request.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Declarative Hue Boundary (Priority: P1)

Operators need a clear instruction that Philips Hue V2 pairing is performed through the Home Assistant UI and stored as runtime state, not declared in Git.

**Why this priority**: This prevents accidental commits of Hue tokens or misleading empty package files while still enabling the integration to be onboarded safely.

**Independent Test**: Review `docs/runbooks/home-assistant.md` and confirm it states that Hue V2 bridge pairing is a runtime config-flow on the PVC and that Git-owned YAML follows only after entity IDs exist.

**Acceptance Scenarios**:

1. **Given** a Home Assistant operator preparing Hue V2, **When** they read the runbook, **Then** they can identify the UI pairing step and know not to commit `.storage`, config entries, tokens, or credentials.

### User Story 2 - Post-Pairing Inventory (Priority: P2)

Operators need to know what inventory to capture after Hue entities are created so future Git-owned packages and automations use real entity IDs.

**Why this priority**: Capturing bridge, light, room, zone, scene, remote, switch, and grouped-light information makes the next automation milestone concrete without pretending the integration can be declared before pairing.

**Independent Test**: Review `docs/runbooks/home-assistant.md` and confirm it lists the Hue inventory to record after pairing.

**Acceptance Scenarios**:

1. **Given** Hue V2 pairing has completed in Home Assistant, **When** the operator follows the runbook, **Then** they record bridge name, light entity IDs, room/zone/grouped-light entities, scenes, remotes/switches, and disabled grouped-light entities worth enabling before adding Git-owned automation YAML.

## Requirements *(mandatory)*

- **FR-001**: The runbook MUST state that Philips Hue V2 bridge pairing is a Home Assistant UI config-flow handshake stored on the `home-assistant-config` PVC.
- **FR-002**: The runbook MUST state that Hue `.storage` entries, config entries, bridge credentials, tokens, and fake integration config are not committed.
- **FR-003**: The runbook MUST list the post-pairing inventory needed before Git-owned Hue packages or automations are added.
- **FR-004**: The implementation MUST NOT add an empty or placeholder Hue package YAML file.
- **FR-005**: Evidence MUST include owner workflow validation, local review checks, grep/diff checks for Hue runtime state and credentials, the development-smoke exception, and branch handoff state.

## Risk And Validation Expectations

**Tiny**: This is a docs-only guidance change plus SDD artifacts. Run the owner workflow validators, SDD context validator, `git diff --check`, and targeted diff/grep checks proving no Hue runtime state or credentials were added. No code TDD or development-cluster smoke is required.

## Success Criteria *(mandatory)*

- **SC-001**: `docs/runbooks/home-assistant.md` contains concise Hue V2 pairing and inventory guidance.
- **SC-002**: `git diff --check` passes.
- **SC-003**: Targeted diff/grep checks show no Hue `.storage`, config entry, token, credential, or placeholder package was added.
- **SC-004**: Workflow owner validators and SDD context validation pass.

## Assumptions

- Hue V2 pairing requires a physical Hue bridge and Home Assistant UI access, so it cannot be validated in the development cluster for this docs-only milestone.
- Future Git-owned Hue packages and automations should be created only after Home Assistant has generated real entity IDs during runtime pairing.

## Open Questions

- None.
