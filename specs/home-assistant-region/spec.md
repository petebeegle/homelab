# Feature Specification: home-assistant-region

**Feature Branch**: `codex/home-assistant-region`
**Created**: 2026-07-03
**Status**: Draft
**Risk Tier**: high
**Input**: User description: "country is not set"

## Summary

Home Assistant should have a complete GitOps-managed home region configuration
so the UI no longer reports that country is unset while `configuration.yaml`
owns the Home Information settings.

## Binding Sources

- `AGENTS.md`
- `.specify/memory/constitution.md`
- `docs/runbooks/implementation-workflow.md`
- `docs/runbooks/spec-driven-development.md`
- `docs/runbooks/add-secret.md`
- `docs/decisions/codex-implementation-workflow.md`
- `docs/decisions/sops-age-secrets.md`

## Scope

### In Scope

- Configure production Home Assistant home information in YAML.
- Store exact production location values in a SOPS-encrypted Kubernetes Secret.
- Mount `/config/secrets.yaml` for Home Assistant `!secret` lookups.
- Add Flux SOPS decryption for the production Home Assistant app.
- Keep development branch environments on non-sensitive regional defaults.
- Document the YAML-owned Home Information behavior.

### Out Of Scope

- Public Gateway or Cloudflare Tunnel exposure changes.
- Runtime `.storage` state.
- Home Assistant device or integration onboarding.

## User Scenarios & Testing

### User Story 1 - Country Is Configured (Priority: P1)

As a Home Assistant operator, I want country and regional settings defined in
GitOps so the Home Information page reflects the intended US/Eastern home setup.

**Why this priority**: The UI cannot edit these fields while `configuration.yaml`
owns the `homeassistant:` key.

**Independent Test**: Render the production app and inspect the mounted
configuration and Secret volume wiring.

**Acceptance Scenarios**:

1. **Given** production Home Assistant renders from GitOps, **When** the app
   reconciles, **Then** `country: US`, `time_zone: America/New_York`,
   `currency: USD`, and `unit_system: us_customary` are present under
   `homeassistant:`.
2. **Given** exact home location values are sensitive, **When** the repository is
   reviewed, **Then** latitude, longitude, and elevation are committed only
   inside a SOPS-encrypted Secret.

## Requirements

- **FR-001**: Production `configuration.yaml` MUST set Home Assistant home
  information for US/Eastern regional behavior.
- **FR-002**: Exact production latitude, longitude, and elevation MUST be loaded
  through `/config/secrets.yaml` and MUST NOT be committed in plaintext.
- **FR-003**: Flux MUST be able to decrypt the Home Assistant app Secret through
  the existing `sops-age` mechanism.
- **FR-004**: Branch environments MUST receive only non-sensitive regional
  defaults unless later validation proves exact location is required.
- **FR-005**: Evidence MUST record workflow validation, SOPS verification, local
  render checks, and development validation or an explicit exception.

## Risk And Validation Expectations

**High**: Use broad local verification and development validation for the
affected app. Record any unavailable infrastructure or credential exception with
substitute checks.

## Success Criteria

- **SC-001**: Rendered production manifests include an encrypted
  `home-assistant-secrets` Secret and a read-only `/config/secrets.yaml` mount.
- **SC-002**: Rendered Home Assistant configuration contains the intended public
  regional defaults and secret references for exact location values.
- **SC-003**: `sops -d kubernetes/apps/home-assistant/secret.yaml` succeeds
  without committing plaintext secret data.
- **SC-004**: Development validation evidence or a documented exception is
  recorded in `specs/home-assistant-region/evidence.md`.

## Assumptions

- Country is `US`, currency is `USD`, time zone is `America/New_York`, unit
  system is `us_customary`, and radius is `100` meters.
- Home Assistant Home Information remains YAML-owned and read-only in the UI.
- Runtime policy blocks delegated implementation ownership in this session, so
  the implementation owner identity records the required workflow files while no
  verifier approval is created.

## Open Questions

- None.
