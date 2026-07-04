# Feature Specification: sdd-dev-smoke-matrix

**Feature Branch**: `codex/sdd-dev-smoke-matrix`
**Created**: 2026-07-03
**Status**: Draft
**Risk Tier**: medium
**Input**: User description: "Expand the config-driven development smoke matrix and generic checks for sdd-dev-smoke-matrix."

## Summary

Development branch smoke validation should prove more app behavior from
config-driven profiles before relying on production synthetic smoke as the first
signal. Operators need reusable profile fields for Flux Kustomization readiness,
TLSRoute readiness, scoped Secret reference presence, route URLs for browser
handoff, and documented app coverage or gaps for apps that cannot be safely
represented in this slice.

## Binding Sources

- `AGENTS.md`
- `.specify/memory/constitution.md`
- `docs/runbooks/implementation-workflow.md`
- `docs/runbooks/spec-driven-development.md`
- `docs/runbooks/development-cluster.md`
- `docs/decisions/codex-implementation-workflow.md`
- `docs/decisions/tdd-and-development-smoke-evidence.md`
- `docs/decisions/cilium-gateway-api-ingress.md`
- `docs/decisions/sops-age-secrets.md`
- `docs/decisions/synology-nfs-storage.md`

## Scope

### In Scope

- Preserve existing dev smoke profile behavior for `whoami`, `jellyfin`, and
  `home-assistant`.
- Add schema and verification support for Flux Kustomization readiness,
  TLSRoute readiness, Kubernetes Secret reference presence, and route URL fields.
- Add tests that cover the new schema/checks and command sequencing.
- Add safe profile and branch overlay support for `pihole` and `foundryvtt` if
  their development-only names, routes, PVCs, and secret references can avoid
  production collisions.
- Investigate `authentik` and `monitoring`; document gaps instead of forcing
  unsafe profile support when dependencies exceed this slice.
- Audit the synthetic smoke source duplication between `tests/smoke` and
  `kubernetes/apps/synthetics/smoke` and either enforce mirroring or document a
  follow-up.
- Update development-cluster and tooling documentation plus implementation
  evidence.

### Out Of Scope

- Production-first live cluster mutations or durable changes outside Git.
- Reading, decrypting, or logging Kubernetes Secret contents.
- Broad application refactors to make complex apps fit smoke profiles.
- Verifier approval artifacts, PR creation, or final verifier sign-off.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Generic Smoke Checks (Priority: P1)

An operator can add a branch smoke profile that verifies Flux Kustomizations,
HTTPRoutes, TLSRoutes, Services, PVC storage classes, referenced Secret names,
and route probes from profile data.

**Why this priority**: Generic checks are the smallest reusable improvement and
unlock later app coverage without one-off scripts.

**Independent Test**: `python3 -m unittest discover -s tools/development/tests`
includes profile parsing and checker sequencing coverage.

**Acceptance Scenarios**:

1. **Given** a profile with kustomizations, tls_routes, secret_refs, and
   route_urls, **When** the branch verifier builds and runs checks, **Then** it
   sequences the new checks without dropping existing namespace, pod,
   HelmRelease, Service, HTTPRoute, PVC, or HTTP probe checks.
2. **Given** a profile secret reference, **When** the secret check runs, **Then**
   it only checks for the referenced Kubernetes Secret name in the namespace and
   never reads or logs Secret data.

### User Story 2 - App Coverage And Gaps (Priority: P2)

An operator can see which development smoke profiles are available and why any
requested app remains documentation-only.

**Why this priority**: Coverage expansion is valuable only if unsafe gaps are
explicit and do not masquerade as verified support.

**Independent Test**: Unit/static checks plus rendered branch overlay review
show safe isolation for any added app profiles.

**Acceptance Scenarios**:

1. **Given** a safe app branch overlay, **When** its smoke profile is rendered,
   **Then** branch-specific names include the branch slug and avoid production
   collisions.
2. **Given** an app that depends on secrets, shared stacks, or broader refactors
   beyond the slice, **When** documentation is updated, **Then** the exact gap
   and follow-up path are recorded.

### User Story 3 - Browser Smoke Handoff (Priority: P3)

An operator has a profile-level route URL field and documented Playwright handoff
for branch hostnames under `dev.lab.petebeegle.com`.

**Why this priority**: Browser smoke is useful for routed apps but should not
force live cluster credentials into unit tests.

**Independent Test**: Profile schema tests and documentation verify the handoff
path; live execution is attempted only when development credentials are
available and safe.

**Acceptance Scenarios**:

1. **Given** a profile route URL, **When** documentation describes validation,
   **Then** it records browser smoke expectations and failure artifact behavior.
2. **Given** live cluster credentials are unavailable, **When** evidence is
   finalized, **Then** the development smoke exception and substitute checks are
   recorded.

## Requirements *(mandatory)*

- **FR-001**: The implementation MUST preserve existing `whoami`, `jellyfin`,
  and `home-assistant` smoke profile behavior.
- **FR-002**: The profile schema and checker MUST support Flux Kustomization
  readiness checks.
- **FR-003**: The profile schema and checker MUST support TLSRoute readiness
  checks without replacing HTTPRoute readiness.
- **FR-004**: The profile schema and checker MUST support Secret reference
  presence checks by Kubernetes Secret name only, without inspecting Secret
  contents.
- **FR-005**: The profile schema or documentation MUST support route URL handoff
  for Playwright smoke under `dev.lab.petebeegle.com`.
- **FR-006**: The implementation MUST add tests for new profile fields, checks,
  and command sequencing where the codebase has test seams.
- **FR-007**: The implementation MUST add safe profile or overlay coverage for
  `pihole` and `foundryvtt`, or document why a profile is unsafe in this slice.
- **FR-008**: The implementation MUST investigate `authentik` and `monitoring`
  and record explicit gaps when profile support requires secrets,
  cross-stack dependencies, or broader refactors.
- **FR-009**: The implementation MUST audit synthetic smoke source duplication
  and either add mirroring enforcement or record a follow-up.
- **FR-010**: Evidence MUST record required command outcomes, development smoke
  results or unavailable-infrastructure exceptions, and final `HEAD`.

## Risk And Validation Expectations

**Medium**: Include focused unit tests for tooling and rendered/static checks
for Kubernetes branch overlays. Attempt development-cluster validation for the
`whoami` branch profile if kube credentials are available and safe; otherwise
document the unavailable-infrastructure exception with substitute checks.

## Success Criteria *(mandatory)*

- **SC-001**: `python3 -m unittest discover -s tools/development/tests` passes
  with coverage for new profile fields and check sequencing.
- **SC-002**: Existing smoke profiles continue to parse and existing checks are
  not removed.
- **SC-003**: Added branch overlays, if any, use `${branch_slug}` in names,
  hostnames, and resources that could collide with production.
- **SC-004**: `docs/runbooks/development-cluster.md`,
  `tools/development/README.md`, and `specs/sdd-dev-smoke-matrix/evidence.md`
  record app coverage, Playwright handoff, synthetic smoke audit, and gaps.

## Assumptions

- No development cluster credentials or local secret staging are assumed at the
  start of implementation.
- Branch smoke pushes are allowed only through the validated implementation clone
  and only for development validation.
- Secret presence checks can use Kubernetes object metadata APIs without
  retrieving or printing secret data payloads.

## Open Questions

- None.
