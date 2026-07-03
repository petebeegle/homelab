# Feature Specification: sdd-synthetic-smoke-mirroring

**Feature Branch**: `codex/sdd-synthetic-smoke-mirroring`
**Created**: 2026-07-03
**Status**: Draft
**Risk Tier**: low
**Input**: User description: "Make shared synthetic smoke route tests mirror between local/manual smoke and in-cluster synthetics, and add a policy guard that catches future drift."

## Summary

Operators should be able to trust that the local/manual smoke suite and the
in-cluster synthetic smoke suite exercise the same shared route probes. The
Home Assistant onboarding and OIDC diagnostic must be present in both copies,
and a repository policy check must fail when required mirrored files drift while
leaving intentional cluster-only wrapper and reporter behavior alone.

## Binding Sources

- `AGENTS.md`
- `.specify/memory/constitution.md`
- `docs/runbooks/implementation-workflow.md`
- `docs/runbooks/spec-driven-development.md`
- `docs/runbooks/synthetic-smoke-tests.md`
- `docs/runbooks/development-cluster.md`
- `docs/decisions/codex-implementation-workflow.md`
- `docs/decisions/tdd-and-development-smoke-evidence.md`
- `docs/decisions/cilium-gateway-api-ingress.md`
- `docs/decisions/sops-age-secrets.md`

## Scope

### In Scope

- Sync shared route test content between `tests/smoke/routes.spec.js` and
  `kubernetes/apps/synthetics/smoke/routes.spec.js`.
- Preserve the Home Assistant onboarding and OIDC guard diagnostic in the shared
  route tests.
- Add a policy check that enforces exact equality for the mirrored route spec
  and package lockfiles.
- Wire the policy check into pre-commit for relevant smoke source and lockfile
  paths.
- Add focused unit tests for the policy check.
- Update synthetic smoke documentation and implementation evidence.

### Out Of Scope

- Production route, Gateway, Flux, or application runtime behavior changes.
- Exact equality enforcement for cluster-only wrapper or reporter files,
  `package.json`, or `playwright.config.js`.
- Reading, decrypting, editing, or validating secrets.
- Creating verifier approval artifacts or a pull request.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Shared Route Parity (Priority: P1)

An operator can run local/manual smoke tests and in-cluster synthetic tests with
the same shared route probes, including the Home Assistant onboarding and OIDC
diagnostic.

**Why this priority**: Route parity is the smallest useful fix and removes the
known gap from the previous smoke matrix work.

**Independent Test**: The mirror policy check compares the required route spec
and lockfile pairs exactly.

**Acceptance Scenarios**:

1. **Given** the local/manual route spec, **When** it is compared to the
   in-cluster route spec, **Then** both files match exactly and include the Home
   Assistant onboarding/OIDC diagnostic.
2. **Given** the two smoke package lockfiles, **When** the policy check runs,
   **Then** it confirms they match exactly.

### User Story 2 - Drift Enforcement (Priority: P2)

A contributor gets a fast repository-policy failure when a required mirrored
smoke file changes on one side without the matching file.

**Why this priority**: The next contributor should learn about the mirroring
contract before review or cluster execution.

**Independent Test**: Focused unit tests exercise passing, route-spec drift, and
lockfile drift cases for the policy command.

**Acceptance Scenarios**:

1. **Given** one mirrored route file is changed without the other, **When** the
   policy command runs, **Then** it exits non-zero and reports the drifting pair.
2. **Given** cluster-only files such as wrapper, reporter, `package.json`, or
   `playwright.config.js` differ, **When** the policy command runs, **Then** it
   does not require those files to match.

### User Story 3 - Operator Documentation (Priority: P3)

An operator adding or debugging smoke probes can see that required shared files
are now policy-enforced mirrors.

**Why this priority**: Documentation prevents the former gap from being
reintroduced as tribal knowledge.

**Independent Test**: Review the synthetic smoke runbook and run repository
documentation/static checks.

**Acceptance Scenarios**:

1. **Given** a contributor adds a probe, **When** they follow the synthetic smoke
   runbook, **Then** it directs them to update mirrored files together and run
   the policy/pre-commit check.

## Requirements *(mandatory)*

- **FR-001**: The implementation MUST make
  `tests/smoke/routes.spec.js` and
  `kubernetes/apps/synthetics/smoke/routes.spec.js` exact mirrors.
- **FR-002**: The mirrored route spec MUST preserve the Home Assistant
  onboarding and OIDC guard diagnostic.
- **FR-003**: The implementation MUST add a policy check that exits non-zero
  when the required mirrored route spec files drift.
- **FR-004**: The implementation MUST add a policy check that exits non-zero
  when the required mirrored package lockfiles drift.
- **FR-005**: The policy check MUST NOT require exact equality for cluster-only
  wrapper or reporter files, `package.json`, or `playwright.config.js`.
- **FR-006**: The policy check MUST be wired into `.pre-commit-config.yaml` for
  relevant mirrored smoke files.
- **FR-007**: Focused tests MUST cover successful parity and drift failures.
- **FR-008**: Documentation MUST replace the documented mirroring gap with the
  new enforcement rule.
- **FR-009**: Evidence MUST record owner workflow validators, focused tests,
  required repository checks, smoke npm checks, final `HEAD`, and any precise
  environment exceptions.

## Risk And Validation Expectations

**Low**: Add focused unit tests for the new policy check, run existing harness
and documentation/tooling checks requested by the implementation, and run smoke
suite npm tests locally. Development-cluster validation is not required because
this implementation changes local test source parity, documentation, and policy
guarding only; it does not change durable cluster desired state or production
routes.

## Success Criteria *(mandatory)*

- **SC-001**: The required mirrored smoke file pairs compare equal.
- **SC-002**: Focused policy unit tests pass and demonstrate drift failure.
- **SC-003**: `pre-commit run --all-files` runs the new mirror policy hook and
  passes.
- **SC-004**: The synthetic smoke runbook documents the enforced mirror rule and
  intentional exclusions.
- **SC-005**: Required validation evidence is recorded with exact commands and
  outcomes.

## Assumptions

- Package lockfiles begin identical and should remain exact mirrors.
- `package.json`, `playwright.config.js`, wrapper scripts, and reporters differ
  intentionally for in-cluster execution and are excluded from exact equality.
- No live cluster credentials or secret material are required for this local
  tooling and test-source parity work.

## Open Questions

- None.
