# Feature Specification: sdd-human-gated-speckit-flow

**Feature Branch**: `codex/sdd-human-gated-speckit-flow`
**Created**: 2026-07-04
**Status**: Draft
**Risk Tier**: low
**Input**: User description: "Repair Homelab SDD Human Gates"

## Summary

Homelab's Spec Kit workflow must treat SDD as a human decision workflow, not a
post-implementation documentation workflow. Future agents should draft and
pause at spec, plan, and task/analysis gates before implementation, then
reconcile evidence after implementation.

## Binding Sources

- `AGENTS.md`
- `.specify/memory/constitution.md`
- `docs/runbooks/spec-driven-development.md`
- `docs/runbooks/implementation-workflow.md`
- `docs/decisions/codex-implementation-workflow.md`
- `docs/decisions/tdd-and-development-smoke-evidence.md`
- Upstream Spec Kit quickstart: `https://github.github.com/spec-kit/quickstart.html`
- Upstream Spec Kit repository: `https://github.com/github/spec-kit`

## Scope

### In Scope

- Define the normal meaningful-work SDD path as staged human gates:
  intent brief, specify/clarify, spec approval, plan/checklist, plan approval,
  tasks/analyze, implementation approval, implement, converge, evidence.
- Preserve lightweight handling for `tiny` and obvious `low` changes when
  skipped gates are recorded as explicit exceptions.
- Update runbooks, Spec Kit templates, workflow YAML, and concise agent guidance
  for future implementations.
- Record this implementation's docs-only validation and upstream conformance
  evidence.

### Out Of Scope

- Adding hard local guard blockers for gate approval evidence.
- Rewriting historical `specs/*` artifacts.
- Changing Kubernetes, Terraform, Flux, Gateway, or application behavior.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Human Gates Precede Implementation (Priority: P1)

As an implementation owner, I can see that meaningful Homelab changes must pass
human review at spec, plan, and task/analysis checkpoints before implementation
starts.

**Why this priority**: It fixes the current implementation-shaped workflow and
keeps future code review anchored to approved intent.

**Independent Test**: Inspect the runbooks and workflow YAML for the sequence
`specify`, `clarify`, spec gate, `plan`, `checklist`, plan gate, `tasks`,
`analyze`, implementation gate, `implement`, `converge`.

**Acceptance Scenarios**:

1. **Given** a normal medium-risk change, **When** an agent follows the runbook,
   **Then** it stops for human spec, plan, and task/analysis approval before
   implementation edits.

### User Story 2 - Lightweight Work Has Explicit Exceptions (Priority: P1)

As a reviewer, I can distinguish intentionally lightweight SDD from missing SDD
gates.

**Why this priority**: Tiny and obvious low-risk work should stay ergonomic
without normalizing silent skipped quality gates.

**Independent Test**: Inspect templates and evidence guidance for skipped
`clarify`, `checklist`, `analyze`, or `converge` exception recording.

**Acceptance Scenarios**:

1. **Given** a tiny wording-only change, **When** clarify or analyze is skipped,
   **Then** evidence records the skipped gate and rationale.

### User Story 3 - Tasks Are Implementation Tasks (Priority: P2)

As an implementation agent, I get task lists that execute an approved plan
instead of listing spec and plan creation as implementation tasks.

**Why this priority**: Tasks should be the handoff after spec and plan gates,
not a place to backfill those gates.

**Independent Test**: Inspect `.specify/templates/tasks-template.md` and confirm
there is no `Spec And Plan` task phase.

**Acceptance Scenarios**:

1. **Given** a generated `tasks.md`, **When** a reviewer reads it, **Then** the
   prerequisites identify approved spec/plan inputs and tasks begin with setup
   or implementation preparation.

## Requirements *(mandatory)*

- **FR-001**: SDD runbooks MUST define SDD as a human decision workflow where
  humans own intent, constraints, and acceptance.
- **FR-002**: Workflow guidance MUST include `clarify`, `checklist`, `analyze`,
  and `converge` in the normal meaningful-work path.
- **FR-003**: Lightweight skipped gates MUST be recorded as explicit exceptions
  in evidence.
- **FR-004**: Spec, plan, tasks, and evidence templates MUST expose gate status
  or gate evidence fields.
- **FR-005**: The task template MUST remove the `Spec And Plan` phase and treat
  spec/plan as prerequisites.
- **FR-006**: The Spec Kit workflow YAML MUST model the full quality-gate
  sequence and review gates.
- **FR-007**: Evidence MUST record docs-only smoke exception, validation
  commands, and upstream conformance review for this implementation.

## Risk And Validation Expectations

**Low**: This changes workflow documentation, templates, and local workflow
metadata only. Run focused local checks and targeted content inspections. No
development-cluster smoke is required because no live app or cluster behavior
changes.

## Success Criteria *(mandatory)*

- **SC-001**: Runbooks describe human-gated SDD before implementation.
- **SC-002**: Templates capture clarify/checklist/analyze/converge status or
  exceptions.
- **SC-003**: `tasks-template.md` no longer has a `Spec And Plan` task phase.
- **SC-004**: Workflow YAML includes clarify, checklist, analyze, implement,
  and converge in the intended order.

## Assumptions

- Use docs-and-evidence enforcement, not hard local blockers.
- Keep the one implementation, one branch, one `specs/<implementation>/`, one
  PR model.
- Do not rewrite historical specs.
- Sibling worktree fallback is acceptable because `/workspaces/homelab-worktrees`
  is not writable in this environment.

## Open Questions

- None.
