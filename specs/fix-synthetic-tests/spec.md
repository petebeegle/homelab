# Feature Specification: fix-synthetic-tests

**Feature Branch**: `codex/fix-synthetic-tests`
**Created**: 2026-07-17
**Status**: Draft
**Risk Tier**: low
**Input**: User description: "fix the synthetic tests"

## Human Gate Status

**Intent Brief**: Fix the repository's synthetic smoke tests so operators can trust local and in-cluster smoke results. Preserve mirrored smoke sources and keep Homepage on the intentional `homepage.${cluster_domain}` route instead of adding a bare root-domain route.

**Clarify Status**: resolved by follow-up user correction: the root route is intentionally absent and the test should target the Homepage subdomain.

**Spec Gate**: approved by user request to fix the tests, with explicit follow-up to avoid adding a root route.

## Summary

Synthetic smoke validation should probe the deployed Homepage dashboard at `homepage.${cluster_domain}`. The bare `${cluster_domain}` route is intentionally not a Homepage route.

## Binding Sources

- `AGENTS.md`
- `.specify/memory/constitution.md`
- `docs/runbooks/implementation-workflow.md`
- `docs/runbooks/spec-driven-development.md`
- `docs/runbooks/synthetic-smoke-tests.md`

## Scope

### In Scope

- Retarget the mirrored Homepage smoke probe to `homepage.${cluster_domain}`.
- Keep local smoke files and in-cluster smoke files mirrored where policy requires exact copies.
- Update nearby operator docs that incorrectly described Homepage as a root-domain route.
- Run focused local validation for the smoke suite and mirroring policy.

### Out Of Scope

- Adding or restoring a bare `${cluster_domain}` Homepage route.
- Changing Gateway resources, Flux wiring, storage, secrets, or production cluster state.
- Broad redesign of synthetic monitoring dashboards or alerting.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Reliable Synthetic Smoke Tests (Priority: P1)

Operators can run synthetic smoke tests and see pass/fail results that reflect the intended routed services rather than a stale root-domain assumption.

**Why this priority**: The smallest useful slice is making the existing smoke suite runnable and accurate without changing desired-state routing.

**Independent Test**: Run the mirror policy check, focused helper tests, and the Playwright smoke tests against the configured base domain.

**Acceptance Scenarios**:

1. **Given** the synthetic smoke sources in the repository, **When** mirror validation runs, **Then** required shared smoke files match exactly.
2. **Given** Homepage is intentionally routed at `homepage.${cluster_domain}`, **When** the smoke test visits Homepage, **Then** it reaches the dashboard on the subdomain.
3. **Given** a smoke run fails before the reporter emits a summary, **When** the wrapper exits, **Then** exactly one fallback summary is emitted and the non-zero exit status is preserved.

## Requirements *(mandatory)*

- **FR-001**: The implementation MUST make the Homepage synthetic smoke probe use `homepage.${cluster_domain}`.
- **FR-002**: The implementation MUST preserve exact mirrors for `tests/smoke/routes.spec.js` and `kubernetes/apps/synthetics/smoke/routes.spec.js`.
- **FR-003**: The implementation MUST preserve synthetic summary behavior for in-cluster smoke jobs.
- **FR-004**: Evidence MUST record focused local commands and final branch state.

## Risk And Validation Expectations

**Low**: Run relevant local checks. Add or update a small test when the change touches executable code and the repo has a reasonable test seam.

## Success Criteria *(mandatory)*

- **SC-001**: `python3 tools/policy/check_synthetic_smoke_mirroring.py` passes.
- **SC-002**: `python3 -m unittest tools.policy.tests.test_check_synthetic_smoke_mirroring` passes.
- **SC-003**: Synthetic smoke Node helper tests pass.
- **SC-004**: Local Playwright smoke tests pass against the current routed services.

## Assumptions

- The user's follow-up correction supersedes the earlier route-repair interpretation.
- Development-cluster validation is not required because the final implementation does not change Kubernetes desired state.

## Open Questions

- None
