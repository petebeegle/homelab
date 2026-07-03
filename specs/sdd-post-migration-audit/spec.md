# Feature Specification: sdd-post-migration-audit

**Feature Branch**: `codex/sdd-post-migration-audit`
**Created**: 2026-07-03
**Status**: Draft
**Risk Tier**: tiny
**Input**: User description: "Make an audit plus cleanup slice: verify Spec Kit routing, classify open PRs, centralize backlog, aggressively prune vestigial .codex/tools documentation."

## Summary

Audit the repository after the SDD migration and remove duplicated Codex-local
guidance so future operators are routed to the canonical workflow sources. The
slice produces durable SDD evidence, a final audit report, and a focused cleanup
of vestigial `.codex` and tool README documentation without changing cluster or
tool behavior.

## Binding Sources

- `AGENTS.md`
- `.specify/memory/constitution.md`
- `docs/runbooks/spec-driven-development.md`
- `docs/runbooks/implementation-workflow.md`
- `docs/decisions/codex-implementation-workflow.md`
- `docs/decisions/tdd-and-development-smoke-evidence.md`
- harness validators under `tools/codex-harness/`

## Scope

### In Scope

- Add durable SDD artifacts and final audit report under
  `specs/sdd-post-migration-audit/`.
- Verify Spec Kit routing and record the canonical guidance boundary.
- Classify currently open PRs and centralize follow-up backlog, including
  `codex/dev-secret-staging-for-smoke`.
- Record ignored `.codex/tmp` residue categories before local cleanup by another
  actor.
- Delete tracked `.codex/memory/approved/*.md` notes that duplicate canonical
  docs and remove `.codex/memory/approved/**/*.md` from retrieval routing.
- Rewrite `.codex/agents/*.toml` as short pointers to canonical docs.
- Prune `.codex/runbooks/README.md` if it only preserves legacy placement.
- Keep `tools/development/README.md` as CLI usage guidance and defer authority to
  `docs/runbooks/development-cluster.md`.

### Out Of Scope

- Implementing the follow-up `codex/dev-secret-staging-for-smoke` branch.
- Editing tool code, tool tests, or docstrings unless they state obsolete
  canonical guidance.
- Purging ignored `.codex/tmp` residue in the planner checkout.
- Creating verifier approval or verifier attestation.
- Changing Kubernetes, Terraform, Flux, secret, or development cluster behavior.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Canonical Guidance Routing (Priority: P1)

As a future Codex operator, I need local agent and retrieval guidance to point at
the current SDD workflow instead of duplicated approved memory notes.

**Why this priority**: It prevents agents from following stale pre-migration
workflow guidance.

**Independent Test**: Run targeted `rg` checks and
`python3 tools/policy/check_retrieval_manifest.py`.

**Acceptance Scenarios**:

1. **Given** the repository guidance files, **When** an operator searches
   `.codex/agents` and `.codex/retrieval.yaml`, **Then** implementation workflow
   details route to canonical docs and approved memory markdown is not retrieved.

### User Story 2 - Durable Audit And Backlog (Priority: P2)

As a maintainer, I need the audit findings and follow-up backlog preserved in the
implementation artifacts.

**Why this priority**: The cleanup is useful only if reviewers can see what was
verified, deferred, and intentionally left untouched.

**Independent Test**: Review `specs/sdd-post-migration-audit/audit-report.md`
for Spec Kit routing, open PR classification, backlog, and ignored residue
categories.

**Acceptance Scenarios**:

1. **Given** the audit report, **When** a reviewer checks the first slice scope,
   **Then** the report lists open PR status, explicit backlog, and residue
   categories without claiming to implement deferred branches.

## Requirements *(mandatory)*

- **FR-001**: The implementation MUST preserve canonical guidance as `AGENTS.md`,
  `docs/runbooks/spec-driven-development.md`,
  `docs/runbooks/implementation-workflow.md`, `docs/decisions/*`, and harness
  validators.
- **FR-002**: The implementation MUST add `spec.md`, `plan.md`, `tasks.md`,
  `evidence.md`, and an audit report under `specs/sdd-post-migration-audit/`.
- **FR-003**: The audit report MUST verify Spec Kit routing, classify open PRs,
  list explicit backlog including the dev smoke blocker follow-up, and record
  ignored residue categories before local cleanup.
- **FR-004**: The implementation MUST delete tracked duplicated approved memory
  markdown and remove `.codex/memory/approved/**/*.md` from
  `.codex/retrieval.yaml`.
- **FR-005**: `.codex/agents/*.toml` MUST remain short pointers that defer
  workflow detail to canonical docs.
- **FR-006**: `.codex/runbooks/README.md` and `tools/development/README.md` MUST
  avoid obsolete canonical authority language.
- **FR-007**: Evidence MUST record docs-only validation, local check outcomes,
  development smoke exception, and final branch state.

## Risk And Validation Expectations

This is a `tiny` SDD change and `docs-only` implementation workflow change. No
code TDD or live development smoke is required because no executable behavior,
Kubernetes manifests, Terraform, Flux wiring, Gateway routes, storage, or secret
references change.

## Success Criteria *(mandatory)*

- **SC-001**: `python3 tools/policy/check_retrieval_manifest.py` passes.
- **SC-002**: `python3 tools/architecture/render.py --check` passes or confirms
  no generated architecture update is needed.
- **SC-003**: Targeted search confirms `.codex/retrieval.yaml` no longer routes
  `.codex/memory/approved/**/*.md`.
- **SC-004**: The final audit report includes Spec Kit routing, PR
  classification, backlog, residue categories, and validation evidence.

## Assumptions

- Open PR state is advisory and may change after the audit timestamp.
- The planner checkout remains untouched for ignored `.codex/tmp` cleanup.
- The first slice should centralize deferred work as backlog rather than
  implementing additional behavior.

## Open Questions

- None.
