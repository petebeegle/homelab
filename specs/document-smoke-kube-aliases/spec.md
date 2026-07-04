# Feature Specification: document-smoke-kube-aliases

**Feature Branch**: `codex/document-smoke-kube-aliases`
**Created**: 2026-07-04
**Status**: Draft
**Risk Tier**: tiny
**Input**: User description: "codex has issues getting the cluster context for testing. document these aliases as a source for running smokes manually as needed."

## Summary

Operators and Codex agents need the synthetic smoke runbook to point at the
existing kube alias source when manual smoke checks require an explicit
development or production cluster context.

## Binding Sources

- `AGENTS.md`
- `.specify/memory/constitution.md`
- `docs/runbooks/spec-driven-development.md`
- `docs/runbooks/implementation-workflow.md`
- `docs/runbooks/synthetic-smoke-tests.md`
- `docs/runbooks/development-cluster.md`

## Scope

### In Scope

- Document `scripts/kube-aliases.sh` in the synthetic smoke manual-run
  workflow.
- Clarify that `kd` and `fd` target development, while `kp` and `fp` target
  production.
- Show production manual synthetic smoke commands using the production
  kubectl alias.
- Add durable SDD artifacts and evidence for the docs-only change.

### Out Of Scope

- Changing `scripts/kube-aliases.sh`.
- Changing synthetic smoke code, CronJob manifests, cluster state, kubeconfig
  files, or Flux behavior.
- Running a live manual smoke Job as part of this docs-only update.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Explicit Smoke Context (Priority: P1)

As an operator or Codex agent, I need the manual smoke runbook to identify the
alias source and commands that select the intended cluster context.

**Why this priority**: This is the smallest useful change that addresses
context confusion without changing cluster behavior.

**Independent Test**: Review the synthetic smoke runbook and run a targeted
search for the alias source and production manual-run commands.

**Acceptance Scenarios**:

1. **Given** a reader needs to run manual synthetic smoke checks, **When** they
   read the Manual Run section, **Then** they can source the aliases, confirm the
   current context, and run production smoke commands through `kp`.

## Requirements *(mandatory)*

- **FR-001**: The synthetic smoke runbook MUST document
  `scripts/kube-aliases.sh` as the source for opt-in Kubernetes and Flux
  aliases.
- **FR-002**: The runbook MUST identify `kd` and `fd` as development helpers
  and `kp` and `fp` as production helpers.
- **FR-003**: The manual production synthetic smoke examples MUST use `kp`
  rather than unqualified `kubectl`.
- **FR-004**: The implementation MUST NOT change Kubernetes desired state,
  cluster state, smoke test code, or alias behavior.
- **FR-005**: Evidence MUST record docs-only validation and the development
  smoke exception.

## Risk And Validation Expectations

**Tiny**: This is a docs-only update. Record review evidence and run focused
documentation/workflow checks. No live development or production smoke is
required because no executable behavior or desired cluster state changes.

## Success Criteria *(mandatory)*

- **SC-001**: `docs/runbooks/synthetic-smoke-tests.md` tells readers to source
  `scripts/kube-aliases.sh` before manual smoke cluster commands.
- **SC-002**: The runbook includes `kd`, `fd`, `kp`, and `fp` role guidance and
  uses `kp` for production `synthetic-smoke` Job, watch, and log examples.
- **SC-003**: Focused documentation search and SDD context validation pass.

## Assumptions

- The scheduled `synthetic-smoke` CronJob is production-oriented unless a
  development-cluster workflow explicitly says otherwise.
- The current alias definitions in `scripts/kube-aliases.sh` are already
  correct and remain the source of truth.

## Open Questions

- None.
