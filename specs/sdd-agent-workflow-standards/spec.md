# Feature Specification: sdd-agent-workflow-standards

**Feature Branch**: `codex/sdd-agent-workflow-standards`
**Created**: 2026-07-04
**Status**: Draft
**Risk Tier**: low
**Input**: User description: "Implement a general SDD-first agent workflow that conforms to repo SDD docs and upstream Spec Kit standards, strongly favors automated smoke testing, and uses fanout for independent work."

## Summary

Agents need clearer workflow standards for Homelab repository changes: durable
Spec Kit artifacts come first, automated smoke is preferred for user-facing and
operational changes, fanout is used where it is safe, and final evidence
distinguishes rendered intent from live verified behavior.

## Binding Sources

- `AGENTS.md`
- `.specify/memory/constitution.md`
- `docs/runbooks/spec-driven-development.md`
- `docs/runbooks/implementation-workflow.md`
- `docs/decisions/codex-implementation-workflow.md`
- `docs/decisions/tdd-and-development-smoke-evidence.md`
- Upstream Spec Kit docs at `https://github.github.com/spec-kit/`
- Upstream Spec Kit repository at `https://github.com/github/spec-kit`

## Scope

### In Scope

- Clarify SDD-first defaults in repo workflow documentation.
- Add smoke, fanout, and post-implementation conformance expectations to
  templates used for future implementation artifacts.
- Record this implementation's SDD and upstream conformance evidence.

### Out Of Scope

- Adding hard CI gates for smoke profiles or route policy.
- Changing Kubernetes manifests or live cluster state.
- Changing the current branch/worktree guard implementation.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - SDD-First Work Starts Consistently (Priority: P1)

An implementation agent can start a repository change and know exactly which
SDD artifacts, tiers, and evidence fields must exist before tracked edits and
before handoff.

**Why this priority**: It prevents ad hoc implementation and keeps future work
reviewable.

**Independent Test**: Review the runbooks and templates, then validate the SDD
artifact set with the repo harness.

**Acceptance Scenarios**:

1. **Given** a new implementation, **When** an agent reads the workflow docs and
   templates, **Then** the agent sees that Spec Kit artifacts are required before
   normal implementation and evidence is required before push/PR handoff.

### User Story 2 - Smoke Is Preferred And Evidence Is Precise (Priority: P1)

An implementation agent can choose validation for routed, deployed, or
user-facing changes without substituting readiness or render checks for
user-path smoke.

**Why this priority**: Recent Homepage work showed that partial signals can be
misreported as user-visible success.

**Independent Test**: Inspect docs/templates for ordered smoke preference,
exception rules, and deployment completion states.

**Acceptance Scenarios**:

1. **Given** a routed or operational change, **When** an agent writes the plan
   and evidence, **Then** automated smoke is the default expectation and any
   skipped smoke has a documented blocker and substitute checks.

### User Story 3 - Fanout Is Safe And Coordinated (Priority: P2)

An implementation agent can identify fanout opportunities without breaking the
single-implementation branch/spec/PR contract.

**Why this priority**: Independent workstreams can reduce slow implementation
cycles when they are coordinated through tasks and evidence.

**Independent Test**: Inspect task template and workflow docs for parallel task
rules, fanout examples, and consolidation into one evidence file.

**Acceptance Scenarios**:

1. **Given** independent seams such as repo inspection, tests, docs, and smoke,
   **When** an agent writes `tasks.md`, **Then** safe fanout tasks are marked
   `[P]` and final results are consolidated in one evidence file.

## Requirements *(mandatory)*

- **FR-001**: The workflow docs MUST state that repo changes use Spec Kit
  artifacts by default and that repo-local workflow sources remain binding when
  stricter than upstream Spec Kit.
- **FR-002**: The plan template MUST require SDD tier, workflow risk tier, smoke
  strategy, fanout targets, exceptions, and post-implementation SDD conformance.
- **FR-003**: The tasks template MUST make fanout/parallel markers explicit and
  require consolidation into one implementation evidence file.
- **FR-004**: The evidence template MUST record command outcomes, SHAs, URLs,
  smoke results, skipped checks, exceptions, final live verification, and
  upstream SDD conformance.
- **FR-005**: Workflow guidance MUST prefer automated smoke evidence for
  user-facing, routed, deployed, or operational changes.
- **FR-006**: Workflow guidance MUST prohibit calling routed or deployed work
  complete from pod readiness, Service probes, render checks, or route
  `Accepted=True` alone.
- **FR-007**: Evidence MUST record this implementation's local checks,
  docs-only smoke exception, and upstream Spec Kit conformance review.

## Risk And Validation Expectations

**Low**: This is workflow documentation and template guidance. Run focused
local checks for SDD context, markdown/content consistency, and generated docs
status. Development smoke is not required because no Kubernetes, Terraform,
Flux, Gateway, app behavior, storage, or secret reference changes are made.

## Success Criteria *(mandatory)*

- **SC-001**: Future implementation templates expose smoke strategy, fanout
  targets, exceptions, and upstream SDD conformance fields.
- **SC-002**: Workflow docs describe automated smoke preference and live
  verification completion states.
- **SC-003**: Evidence records local checks, the docs-only smoke exception, and
  upstream Spec Kit conformance sources.

## Assumptions

- Repo-local SDD docs and ADRs are binding when stricter than upstream Spec Kit.
- This change is documentation/template guidance and does not need live
  development-cluster smoke.
- Fanout means coordinated independent workstreams, not multiple conflicting
  implementations inside one branch.

## Open Questions

- None.
