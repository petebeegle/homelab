# Feature Specification: adopt-speckit-worktree-flow

**Feature Branch**: `codex/adopt-speckit-worktree-flow`
**Created**: 2026-07-03
**Status**: Draft
**Input**: Replace the custom attested implementation workflow with standard
Spec Kit workflow and default worktree isolation.

## Binding Context

- `AGENTS.md`
- `.specify/workflows/speckit/workflow.yml`
- `.specify/memory/constitution.md`
- `docs/runbooks/spec-driven-development.md`
- `docs/runbooks/implementation-workflow.md`
- `docs/decisions/codex-implementation-workflow.md`

## User Stories

### User Story 1 - Start Concurrent Work In Worktrees

As an operator, I want repository-changing requests to default to a dedicated
worktree so multiple implementations can run concurrently without colliding.

**Acceptance Scenarios**

1. **Given** a repo-changing prompt without an explicit execution mode,
   **When** Codex displays workflow guidance, **Then** the guidance says the
   default is a worktree under `/workspaces/homelab-worktrees/<implementation>`.
2. **Given** a tracked edit is attempted on `main`, **When** the guard runs,
   **Then** the edit is rejected.
3. **Given** a tracked edit is attempted on `codex/<implementation>` with
   matching Spec Kit artifacts, **When** the guard runs, **Then** the edit is
   allowed.

### User Story 2 - Use Standard Spec Kit Implementation

As an implementation agent, I want the repo guidance and templates to route me
through `specify -> plan -> tasks -> implement` without local owner/verifier
attestation boilerplate.

**Acceptance Scenarios**

1. **Given** a new implementation, **When** the agent reads AGENTS and SDD docs,
   **Then** Spec Kit is the canonical implementation flow.
2. **Given** push or PR automation runs from a valid `codex/<implementation>`
   branch, **When** `specs/<implementation>/evidence.md` is present, **Then**
   local verifier attestation files are not required.

## Requirements

- **FR-001**: The workflow MUST use Spec Kit artifacts as the durable
  implementation context.
- **FR-002**: The workflow MUST default tracked repo changes to a dedicated
  worktree unless the user explicitly requests current-checkout or clone mode.
- **FR-003**: The guard MUST reject tracked edits on `main`.
- **FR-004**: The guard MUST reject tracked edits on branches not matching
  `codex/<implementation>`.
- **FR-005**: The guard MUST require matching non-empty `spec.md`, `plan.md`,
  and `tasks.md` after initial Spec Kit artifact bootstrap.
- **FR-006**: Push and PR automation MUST require non-empty matching
  `evidence.md` and MUST NOT require local verifier approval or attestation.
- **FR-007**: Guidance and templates MUST stop requiring active implementation
  markers, implementation plans, owner attestations, verifier attestations, or
  delegation tokens.

## Out Of Scope

- Kubernetes, Terraform, Flux, Gateway, or application manifest changes.
- Changing Spec Kit upstream behavior.
- Requiring GitHub branch protection configuration in this repository change.
