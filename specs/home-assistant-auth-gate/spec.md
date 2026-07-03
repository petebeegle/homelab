# Feature Specification: home-assistant-auth-gate

**Feature Branch**: `codex/home-assistant-auth-gate`
**Created**: 2026-07-03
**Status**: Draft
**Risk Tier**: high
**Input**: User description: "Home Assistant was merged and production is now running, but `https://homeassistant.lab.petebeegle.com/` lands on `/onboarding.html`; scheduled synthetic smoke fails because it expected Authentik/OIDC. HA logs also show an invalid hyphenated package slug and recommend `code_first`. Fix repository-side safety issues so Home Assistant is not exposed over WireGuard/external Gateway while onboarding is present, clear the invalid package slug, and keep smoke failing onboarding clearly."

## Summary

Home Assistant must skip first-run onboarding through GitOps-owned storage seeding so root traffic goes to Authentik/OIDC, including over the WireGuard service-plane route. Repository manifests must also generate the valid `code_first` package slug, and production smoke must continue to fail onboarding with an explicit diagnostic instead of treating it as success.

## Binding Sources

- `AGENTS.md`
- `.specify/memory/constitution.md`
- `docs/runbooks/implementation-workflow.md`
- `docs/runbooks/spec-driven-development.md`
- `docs/decisions/codex-implementation-workflow.md`
- `docs/decisions/tdd-and-development-smoke-evidence.md`
- `docs/runbooks/home-assistant.md`
- `docs/runbooks/development-cluster.md`

## Scope

### In Scope

- Seed Home Assistant onboarding-complete storage in production and branch overlays so fresh PVCs do not serve `/onboarding.html`.
- Restore Home Assistant production exposure through `gateway/external` while keeping the `gateway/internal` route.
- Rename Home Assistant package file and generated ConfigMap keys to `code_first.yaml` in base and branch overlays.
- Update production synthetic smoke so `/onboarding.html` is reported as an explicit failure before the OIDC/AuthentiK URL assertion.
- Update Home Assistant operator docs and generated architecture if route output changes.
- Record local validation and any development-cluster exception.

### Out Of Scope

- Completing Home Assistant onboarding.
- Changing Authentik provider blueprints, OIDC client secrets, or user/group mappings.
- Creating local Home Assistant recovery credentials.
- Creating verifier approval or opening a pull request.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Gate External Exposure Through OIDC (Priority: P1)

Operators need Home Assistant reachable on the WireGuard service-plane Gateway without exposing first-run onboarding.

**Why this priority**: This is the smallest safety correction that restores expected access while keeping onboarding from being exposed.

**Independent Test**: Render `kubernetes/apps/home-assistant` and confirm the Deployment mounts `/config/.storage/onboarding` and the HTTPRoute references both `gateway/internal` and `gateway/external`.

**Acceptance Scenarios**:

1. **Given** the production Home Assistant app manifests, **When** they are rendered, **Then** the Home Assistant pod receives a storage seed marking onboarding done and the HTTPRoute attaches to both internal and external Gateways.

### User Story 2 - Valid Package Slug (Priority: P1)

Operators need Home Assistant package configuration to load without the invalid hyphenated slug warning.

**Why this priority**: The invalid slug is a runtime configuration error in the merged production app.

**Independent Test**: Render base and branch Home Assistant kustomizations and grep the repository and rendered output for absence of the invalid hyphenated slug.

**Acceptance Scenarios**:

1. **Given** base and branch Home Assistant kustomizations, **When** config maps are generated, **Then** package keys and paths use `code_first.yaml`.

### User Story 3 - Clear Synthetic Failure (Priority: P2)

Operators need scheduled smoke to explain that onboarding is unsafe and incomplete while still expecting OIDC/AuthentiK as the success path.

**Why this priority**: The existing smoke failure is correct but not diagnostic enough during first-run recovery.

**Independent Test**: Run the synthetic smoke test suite and review the Home Assistant assertion.

**Acceptance Scenarios**:

1. **Given** Home Assistant serves `/onboarding.html`, **When** production synthetic smoke runs, **Then** the Home Assistant test fails with a message to confirm the GitOps onboarding seed is mounted and Authentik OIDC is verified.

## Requirements *(mandatory)*

- **FR-001**: The production and branch Home Assistant Deployments MUST mount a ConfigMap-owned `/config/.storage/onboarding` file whose Home Assistant storage JSON uses version `4`, key `onboarding`, and a `done` list containing `user`, `core_config`, `analytics`, and `integration`.
- **FR-002**: Base and branch Home Assistant package ConfigMap keys and source file paths MUST use `code_first.yaml`, with no remaining references to the old hyphenated package file.
- **FR-003**: Production synthetic smoke MUST keep Authentik/OIDC as the Home Assistant success expectation and MUST fail onboarding with a clear diagnostic.
- **FR-004**: The production Home Assistant HTTPRoute MUST attach to both `gateway/internal` and `gateway/external` after onboarding is code-seeded complete.
- **FR-005**: Home Assistant docs or PR summary MUST note that no local credential exists until an owner creates one later.
- **FR-006**: Evidence MUST include local render checks, synthetic tests, architecture render write/check, targeted grep/render assertions, and development validation or a precise exception.

## Risk And Validation Expectations

**High**: This change touches authentication expectations and production traffic exposure. Use broad local render and smoke checks, refresh generated architecture, and run development validation for Home Assistant with `--include-cluster-base` when credentials and branch deployment support are available. If development validation is unavailable, record the blocker and substitute local render/smoke checks.

## Success Criteria *(mandatory)*

- **SC-001**: `kubectl kustomize kubernetes/apps/home-assistant` and `kubectl kustomize kubernetes/apps/home-assistant/branch` render Home Assistant Deployments with `/config/.storage/onboarding` mounted from a ConfigMap.
- **SC-002**: `kubectl kustomize kubernetes/apps/home-assistant/branch` renders package ConfigMap data keyed by `code_first.yaml`.
- **SC-003**: `kubectl kustomize kubernetes/apps/home-assistant` renders a Home Assistant HTTPRoute with both `gateway/internal` and `gateway/external`.
- **SC-004**: `npm --prefix kubernetes/apps/synthetics/smoke test` is run and recorded.
- **SC-005**: `python3 tools/architecture/render.py --check` passes after any generated architecture refresh.

## Assumptions

- Onboarding is intentionally not completed by repository changes and must be performed through Home Assistant runtime UI.
- Development branch validation may be limited because the development cluster does not run Authentik, as documented in `docs/runbooks/development-cluster.md`.

## Open Questions

- None.
