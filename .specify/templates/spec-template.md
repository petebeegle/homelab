# Feature Specification: [IMPLEMENTATION]

**Feature Branch**: `codex/[IMPLEMENTATION]`
**Created**: [DATE]
**Status**: Draft
**Risk Tier**: [tiny|low|medium|high]
**Input**: User description: "$ARGUMENTS"

## Human Gate Status

**Intent Brief**: [Outcome, affected users/systems, constraints, non-goals,
risks, and acceptance signals supplied by the human.]

**Clarify Status**: [run with summary | skipped with rationale]

**Spec Gate**: [pending human approval | approved by <who/context> | rejected]

## Summary

[State the intended operator/user outcome in plain language. Avoid implementation
details unless they are constraints from binding ADRs or runbooks.]

## Binding Sources

- `AGENTS.md`
- `.specify/memory/constitution.md`
- `docs/runbooks/implementation-workflow.md`
- [Add relevant ADRs and runbooks for this implementation]

## Scope

### In Scope

- [Capability, behavior, document, or artifact included in this PR]

### Out Of Scope

- [Explicit non-goal or deferred follow-up]

## User Scenarios & Testing *(mandatory)*

### User Story 1 - [Brief Title] (Priority: P1)

[Describe the independently valuable outcome.]

**Why this priority**: [Explain why this is the smallest useful slice.]

**Independent Test**: [Describe the local, development-cluster, or review check
that proves this story independently.]

**Acceptance Scenarios**:

1. **Given** [initial state], **When** [action], **Then** [expected outcome]

### User Story 2 - [Brief Title] (Priority: P2)

[Omit if the implementation has only one meaningful story.]

**Why this priority**: [Explain value.]

**Independent Test**: [Describe independent verification.]

**Acceptance Scenarios**:

1. **Given** [initial state], **When** [action], **Then** [expected outcome]

## Requirements *(mandatory)*

- **FR-001**: The implementation MUST [observable requirement].
- **FR-002**: The implementation MUST preserve [binding invariant].
- **FR-003**: Evidence MUST record [required command, smoke check, or exception].

Use `[NEEDS CLARIFICATION: question]` only when the implementation cannot be
planned safely with existing ADRs, runbooks, or user instructions.

## Risk And Validation Expectations

**Tiny**: Record the review check. Run focused checks only when the edited file
has a cheap validator.

**Low**: Run relevant local checks. Add or update a small test when the change
touches executable code and the repo has a reasonable test seam.

**Medium**: Include focused render/unit tests and development-cluster validation
for covered Kubernetes, Terraform, Flux, Gateway, storage, secret reference,
branch overlay, or app behavior changes. Document unavailable-infrastructure
exceptions with substitute checks.

**High**: Use helper lanes where available, include broader local verification,
and run development validation for affected apps or shared base paths. Include
`--include-cluster-base` when the development base must reconcile first.

## Success Criteria *(mandatory)*

- **SC-001**: [Measurable outcome, command result, or reviewable artifact state]
- **SC-002**: [Measurable outcome, command result, or reviewable artifact state]

## Assumptions

- [Assumption chosen from existing ADRs/runbooks/user instructions]

## Open Questions

- [Question or `None`]
