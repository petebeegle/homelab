# Feature Specification: sdd-workflow-guards

**Feature Branch**: `codex/sdd-workflow-guards`
**Created**: 2026-07-03
**Status**: Draft
**Risk Tier**: low
**Input**: User description: "Teach workflow guards and PR creation to require durable SDD context, exact verifier evidence, and a narrow development smoke push exception."

## Summary

Workflow automation must treat `specs/<implementation>/` as the durable planning
and evidence record for implementation work. Local scratch files under
`.codex/tmp/` remain required for active runtime state, but non-bootstrap tracked
edits, verifier handoff, and automatic PR creation should fail when required SDD
artifacts or exact-HEAD evidence are missing or stale.

## Binding Sources

- `AGENTS.md`
- `.specify/memory/constitution.md`
- `docs/runbooks/implementation-workflow.md`
- `docs/runbooks/spec-driven-development.md`
- `docs/decisions/codex-implementation-workflow.md`
- `docs/decisions/tdd-and-development-smoke-evidence.md`

## Scope

### In Scope

- Require non-empty `spec.md`, `plan.md`, and `tasks.md` in
  `specs/<implementation>/` for non-bootstrap tracked edits.
- Require `evidence.md` before verifier approval or automatic PR creation, with
  stale-HEAD rejection where evidence declares a final or approved HEAD.
- Move PR creation self-checks into `.codex/scripts/create_implementation_pr.sh
  --auto` so PR creation performs its own workflow gates.
- Preserve exact-HEAD verifier approval for final handoff and PR creation.
- Permit only the development smoke push pattern needed to push
  `codex/<implementation>` from a valid active implementation clone and SDD
  context.
- Add focused automated checks and documentation for the enforced behavior.

### Out Of Scope

- Repo-local skill cleanup.
- Development smoke matrix expansion.
- Removing old untracked files from the main checkout.
- Broad workflow rewrites beyond guard enforcement.
- Creating verifier approval or opening the PR from this implementation owner
  pass.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Durable SDD Context Is Required (Priority: P1)

An implementation owner cannot continue non-bootstrap tracked edits unless the
branch has durable SDD planning artifacts.

**Why this priority**: This is the smallest useful guard against losing design
context in ignored runtime files.

**Independent Test**: Focused harness tests cover valid, missing, and empty SDD
artifact combinations.

**Acceptance Scenarios**:

1. **Given** a valid implementation marker and owner attestation, **When** a
   non-bootstrap tracked edit is attempted without `spec.md`, `plan.md`, or
   `tasks.md`, **Then** the workflow guard exits non-zero with a useful message.
2. **Given** non-empty `spec.md`, `plan.md`, and `tasks.md`, **When** the same
   tracked edit is checked, **Then** the SDD context gate passes.

### User Story 2 - PR Creation Self-Gates (Priority: P1)

Automatic PR creation must not depend on a separate Stop hook to catch missing
verifier evidence.

**Why this priority**: PR creation is the durable boundary where exact verifier
approval and evidence need to be checked deterministically.

**Independent Test**: Script tests exercise `create_implementation_pr.sh --auto`
with missing and valid exact-HEAD verifier approval, verifier attestation, and
`evidence.md`.

**Acceptance Scenarios**:

1. **Given** a branch without exact-HEAD verifier approval or verifier
   attestation, **When** `create_implementation_pr.sh --auto` runs, **Then** it
   fails before pushing or creating a PR.
2. **Given** a branch where `evidence.md` records a final HEAD that differs from
   branch `HEAD`, **When** PR gates run, **Then** the stale evidence is rejected.

### User Story 3 - Smoke Push Exception Is Narrow (Priority: P2)

Development validation can push an active implementation branch for smoke
testing without weakening final verifier approval.

**Why this priority**: Branch smoke validation needs a pre-verifier push, while
handoff and PR creation still need exact verifier evidence.

**Independent Test**: Push guard tests cover allowed active
`codex/<implementation>` smoke pushes and rejected invalid branch/context pushes.

**Acceptance Scenarios**:

1. **Given** a valid implementation clone, active `codex/<implementation>`
   branch, owner attestation, and SDD context, **When** a push targets
   `origin codex/<implementation>` for development smoke, **Then** the push
   guard allows it before verifier approval.
2. **Given** any non-smoke branch or invalid implementation context, **When** a
   push is checked without exact-HEAD verifier approval, **Then** the push guard
   rejects it.

## Requirements *(mandatory)*

- **FR-001**: The implementation MUST add or update guard validation for
  non-empty `specs/<implementation>/spec.md`, `plan.md`, and `tasks.md` before
  non-bootstrap tracked edits.
- **FR-002**: The implementation MUST require `specs/<implementation>/evidence.md`
  before verifier approval or PR creation, or explicit deferred/unavailable
  evidence text where applicable.
- **FR-003**: Automatic PR creation MUST perform its own exact-HEAD verifier
  approval, verifier attestation, and SDD evidence gates.
- **FR-004**: The smoke push exception MUST apply only to pushes of the active
  `codex/<implementation>` branch from a valid implementation clone and SDD
  context.
- **FR-005**: Final PR creation, final handoff, and non-smoke pushes MUST
  continue to require exact-HEAD verifier approval.
- **FR-006**: Automated checks MUST cover valid/invalid SDD artifacts, PR gate
  failures, smoke push allowance/rejection, and stale evidence when practical.
- **FR-007**: Evidence MUST record commands run, outcomes, docs impact, final
  branch, and final `HEAD`.

## Risk And Validation Expectations

**Low**: This changes local harness, hook, and script behavior. Add focused unit
tests around changed executable paths and run broader local checks that are
feasible. Development-cluster validation is not required because no Kubernetes,
Terraform, Flux, Gateway, storage, secret reference, or app behavior changes are
included.

## Success Criteria *(mandatory)*

- **SC-001**: `python3 -m unittest discover -s tools/codex-harness/tests` passes
  with new SDD, PR gate, and push guard coverage.
- **SC-002**: `.codex/scripts/create_implementation_pr.sh --auto` has testable
  internal workflow gates and does not rely on a Stop hook for PR blocking.
- **SC-003**: Documentation describes the durable SDD artifact gates and smoke
  push exception without expanding the workflow beyond this PR scope.
- **SC-004**: Final branch has no tracked `.codex/tmp/*` runtime files.

## Assumptions

- Spec Kit scaffolding from PR #317 is already present on `origin/main`.
- Development validation pushes target the implementation branch
  `codex/<implementation>` and are distinguishable from final PR creation or
  non-smoke pushes by guard mode or command context.
- Evidence freshness can be checked when `evidence.md` declares a final,
  approved, or branch `HEAD`; otherwise the guard only enforces that evidence is
  present and non-empty.

## Open Questions

- None
