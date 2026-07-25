# Feature Specification: Access Broker Delivery Roadmap

**Feature Branch**: `codex/access-broker-roadmap`
**Created**: 2026-07-25
**Status**: Approved
**Risk Tier**: low
**Input**: User description: "Create a plan for parallel work across all
remaining access-broker actions and produce a plan."

## Human Gate Status

**Intent Brief**: Produce a durable, dependency-aware roadmap for completing the
Discord-driven Authentik and VPN access broker. The roadmap must maximize safe
parallel work while preserving security, GitOps, review, and end-to-end smoke
gates.

**Clarify Status**: Completed as a roadmap-level ambiguity review. Product
choices that do not block portfolio sequencing are retained as explicit
decision gates for the owning implementation rather than silently selected.

**Spec Gate**: Approved by the user on 2026-07-25 with the instruction to fan
out agents and implement the specification.

## Summary

Define the remaining work needed to turn the currently functioning
request-and-approval prototype into a service that safely delivers access to
requesters, creates usable identities, restricts intake, supports revocation and
expiration, survives restarts, protects sensitive configuration, and provides
auditable operations. Decompose that work into independently reviewable
implementation slices with explicit dependencies, parallel lanes, acceptance
signals, and rollout gates.

## Binding Sources

- `AGENTS.md`
- `.specify/memory/constitution.md`
- `docs/runbooks/implementation-workflow.md`
- `docs/runbooks/spec-driven-development.md`
- `docs/decisions/flux-gitops-source-of-truth.md`
- `docs/decisions/sops-age-secrets.md`
- `docs/decisions/tdd-and-development-smoke-evidence.md`
- `docs/runbooks/development-cluster.md`
- `specs/access-broker-foundation/`
- `specs/access-broker-manual-smoke/`
- `specs/access-broker-authentik-token/`
- `specs/access-broker-wgeasy-provisioning/`

## Scope

### In Scope

- Inventory all known remaining requester, identity, authorization, lifecycle,
  persistence, security, observability, deployment, testing, and documentation
  work.
- Define a dependency graph and delivery waves that expose safe parallel work.
- Define one implementation name, branch, PR boundary, acceptance signal, and
  smoke expectation for every roadmap slice, plus matching Spec Kit artifacts
  for slices that change `homelab`.
- Identify shared-file and shared-state collision points that require serialized
  integration.
- Preserve unresolved product choices as named decision gates with owners and
  deadlines.
- Define completion criteria for prototype, minimum viable service, and
  production-ready milestones.

### Out Of Scope

- Implementing application, Kubernetes, Authentik, Discord, WireGuard,
  observability, or deployment changes.
- Rotating live credentials or mutating production resources.
- Selecting an Authentik activation model without human approval.
- Treating pod readiness or manifest rendering alone as end-to-end acceptance.
- Combining all remaining work into one branch or pull request.

## User Scenarios & Testing

### User Story 1 - Prioritized Delivery Sequence (Priority: P1)

As the homelab operator, I can see which work must happen first, which work can
run concurrently, and which gates must pass before the service is offered to
other users.

**Why this priority**: The current prototype works for an approving admin but
does not yet provide a complete or revocable requester lifecycle.

**Independent Test**: Review the roadmap dependency graph and verify every
critical gap has exactly one owning slice, prerequisite set, and acceptance
signal.

**Acceptance Scenarios**:

1. **Given** the current deployed prototype, **When** the roadmap is reviewed,
   **Then** requester delivery, usable Authentik login, intake restriction,
   sensitive-data cleanup, revocation, expiration, durability, and operational
   readiness all have explicit owners and ordering.
2. **Given** a slice whose prerequisite is incomplete, **When** contributors
   inspect the roadmap, **Then** the slice is visibly blocked and is not listed
   as safe parallel work.

### User Story 2 - Conflict-Aware Parallel Work (Priority: P2)

As a contributor coordinating multiple agents or engineers, I can start
independent lanes without creating overlapping branches, contradictory state
migrations, or repeated edits to central integration files.

**Why this priority**: Most remaining capabilities touch shared request state
and command handling, so nominal parallelism can create expensive merge and
behavior conflicts.

**Independent Test**: For every parallel wave, compare declared write scopes
and confirm concurrent slices either use disjoint repositories/files or defer
shared integration to a named serialization task.

**Acceptance Scenarios**:

1. **Given** two slices in the same wave, **When** their write scopes are
   compared, **Then** overlapping central files are absent or assigned to a
   single integration owner.
2. **Given** module work that can proceed independently, **When** it reaches an
   integration boundary, **Then** contract tests define the expected behavior
   before shared server wiring begins.

### User Story 3 - Verifiable Incremental Releases (Priority: P3)

As a reviewer, I can approve and deploy each slice independently because its
risk, rollback, development validation, production smoke, and evidence
requirements are explicit.

**Why this priority**: The workflow crosses identity, secrets, public routing,
VPN access, and persistent state; partial success must not be mistaken for a
usable or secure release.

**Independent Test**: Sample each roadmap wave and verify every deployable slice
has a user-facing or operator-facing acceptance test, a rollback or failure
path, and the required Spec Kit and evidence artifacts.

**Acceptance Scenarios**:

1. **Given** a user-facing slice, **When** it is marked complete, **Then** its
   exact Discord, Authentik, VPN, or download path has been tested rather than
   inferred from readiness.
2. **Given** a security-sensitive slice, **When** development infrastructure is
   unavailable, **Then** the roadmap requires a documented exception and the
   strongest safe substitute check before production rollout.

## Requirements

- **FR-001**: The roadmap MUST cover requester delivery, Authentik activation,
  intake authorization, access groups or policy, status and administrative
  commands, revocation, expiration, repeat-request behavior, sensitive-data
  cleanup, durable jobs and storage, auditing, metrics and alerts, immutable
  delivery, command registration, end-to-end smoke, and operator documentation.
- **FR-002**: Every capability MUST map to one independently reviewable
  implementation slice with a unique implementation name and proposed PR
  boundary.
- **FR-003**: The roadmap MUST declare each slice's prerequisites, owning
  repository, scope, parallel boundary, risk tier, and completion signal. The
  slice contract MUST require downstream dependents, exact write scope, local
  validation, development validation, rollback, and completion evidence before
  that slice's own spec gate.
- **FR-004**: The roadmap MUST distinguish module work that can run in parallel
  from shared integration work that must be serialized.
- **FR-005**: Parallel slices MUST NOT share ownership of central command
  dispatch, request-state migration, or production rollout files in the same
  wave.
- **FR-006**: The roadmap MUST establish a foundation wave before feature
  fanout when multiple capabilities depend on the same persistence model,
  lifecycle state machine, or service boundaries.
- **FR-007**: The requester MUST have a reliable private retrieval path that
  does not require the approving administrator to forward credentials.
- **FR-008**: The identity activation implementation MUST be blocked by a human
  decision between linked identity and temporary password setup models, with
  security and recovery consequences documented.
- **FR-009**: The roadmap MUST require restriction of requests to configured
  Discord installation contexts before access is offered beyond the test
  operator.
- **FR-010**: The roadmap MUST require revocation to remove or disable VPN
  access and deactivate only broker-owned identity authorization without
  deleting unrelated identity data.
- **FR-011**: The roadmap MUST require sensitive VPN configurations and bearer
  tokens to be removed after consumption or expiry and must define retention
  for audit-safe metadata.
- **FR-012**: The roadmap MUST require idempotent retry behavior and recovery
  from process restart during provisioning, delivery, revocation, and cleanup.
- **FR-013**: Every future implementation MUST follow one branch and one
  repository PR. Implementations that change `homelab` MUST also use one
  matching Spec Kit directory and one consolidated evidence record; app-only
  PRs MUST record equivalent test and smoke evidence in the PR.
- **FR-014**: Cluster desired-state changes MUST flow through Git and Flux;
  secrets MUST remain SOPS-encrypted; ingress MUST remain Gateway API based.
- **FR-015**: User-facing or operational slices MUST include automated
  development or synthetic smoke when practical and document any unverified
  layer precisely.

## Edge Cases

- The requester blocks Discord direct messages or leaves the guild before
  approval.
- Approval completes after the original request interaction token expires.
- Two administrators approve, deny, or revoke the same request concurrently.
- Authentik succeeds while VPN provisioning fails, or the reverse operation
  fails during revocation.
- A pod restarts after an external side effect but before local state commits.
- A download token expires before the requester retrieves it.
- A requester repeats a request after approval, revocation, or peer rotation.
- A username changes while the stable Discord user identity remains the same.
- Development cannot represent the production Discord or public routing path.
- An immutable image is published but Flux has not yet fetched or applied the
  corresponding desired-state revision.

## Key Entities

- **Roadmap Slice**: A future implementation with name, owner, repository,
  scope, prerequisites, dependents, risk, write set, tests, smoke, rollback, and
  evidence.
- **Delivery Wave**: A set of slices that may proceed concurrently after all
  wave prerequisites pass.
- **Decision Gate**: A human-owned choice that blocks one or more slices and
  records alternatives, selection criteria, and deadline.
- **Integration Gate**: A serialized checkpoint that combines completed module
  work into shared command, state, or deployment surfaces.
- **Milestone**: A user-visible readiness level with cumulative acceptance
  criteria.

## Risk And Validation Expectations

This roadmap artifact is low-risk, docs-only planning work. The implementations
it defines will generally be medium or high risk because they affect
authentication, secret handling, persistent state, public traffic, and VPN
authorization. Each slice must independently declare and satisfy its applicable
risk-tier validation rather than inheriting this roadmap's low tier.

## Success Criteria

- **SC-001**: Every capability listed in FR-001 maps to at least one roadmap
  slice and no roadmap slice lacks an owning requirement.
- **SC-002**: Every roadmap slice includes the roadmap fields required by
  FR-003, and the slice contract includes every field required before a
  future slice's spec gate.
- **SC-003**: Every parallel wave has a documented conflict audit and a named
  integration owner for any shared surface.
- **SC-004**: The critical path from current prototype to minimum viable service
  is explicit and contains no unresolved dependency cycle.
- **SC-005**: Prototype, minimum viable service, and production-ready milestones
  each have measurable acceptance criteria.
- **SC-006**: Spec, plan, tasks, requirements checklist, roadmap checklist, and
  cross-artifact analysis contain no critical consistency findings before
  implementation authorization.

## Assumptions

- `petebeegle/homelab-access` remains the application source repository.
- `petebeegle/homelab` remains the desired-state, Authentik blueprint, secret,
  observability, and deployment repository.
- The current request, approval, Authentik user creation, wg-easy provisioning,
  deferred Discord response, and preview-safe one-time download behavior remain
  the starting baseline.
- A requester-triggered private status/retrieval command is the reliable
  baseline delivery mechanism; Discord direct messages may be added as a
  convenience only after bot-token rotation and fallback behavior are defined.
- Stable Discord user IDs remain the identity key even when display names
  change.
- Future access is deny-by-default outside configured guild and channel
  contexts.

## Open Questions

- **DG-001**: Should approved Authentik identities use Discord-linked sign-in or
  a temporary password-setup link? This must be approved before the identity
  activation slice begins.
- **DG-002**: What default access lifetime should apply before automatic
  revocation? This must be approved before lifecycle policy implementation.
- **DG-003**: Which Authentik applications or groups constitute the initial
  access bundle? This must be approved before authorization policy bindings.
