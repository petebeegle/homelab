# Feature Specification: sdd-skill-doc-cleanup

**Feature Branch**: `codex/sdd-skill-doc-cleanup`
**Created**: 2026-07-03
**Status**: Draft
**Risk Tier**: low
**Input**: User description: "Clean stale/overlapping agent docs and config after the Spec Kit + guards migration."

## Summary

Operators should see a single coherent set of repo-local agent guidance after
the Spec Kit and workflow guard migration. Tracked agent skills, custom agent
configuration, retrieval context, approved memory, and transitional planning
documents should either remain current or be retired from default context.

## Binding Sources

- `AGENTS.md`
- `.specify/memory/constitution.md`
- `docs/runbooks/spec-driven-development.md`
- `docs/runbooks/implementation-workflow.md`
- `docs/decisions/codex-implementation-workflow.md`

## Scope

### In Scope

- Audit tracked `.agents/skills/`, `.codex/agents/`, `.codex/memory/approved/`,
  `.codex/retrieval.yaml`, `AGENTS.md`, `PLANS.md`, and related runbooks for
  stale or overlapping agent guidance.
- Keep generated Spec Kit skills tracked on `origin/main`.
- Update custom project agent TOML schema keys when tracked files still use the
  stale `instructions` key.
- Reverify or archive approved memory entries so no approved memory keeps an
  expired `review_after` date.
- Remove or update dead default-context references, especially completed
  migration plans that no longer need to be read by default.
- Record decisions, command evidence, final `HEAD`, documentation impact, and
  exceptions in implementation evidence and PR summary notes.

### Out Of Scope

- Untracked local homelab skills from the main checkout, including `add-app`,
  `add-secret`, `diagnose-*`, and `upgrade-talos`, unless this branch already
  tracks them.
- Kubernetes, Terraform, Flux, storage, Gateway, secret, or live-cluster
  desired-state changes.
- Verifier approval or PR creation.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Current Agent Context (Priority: P1)

An operator starting in the repository can rely on the default agent guidance and
retrieval context without being routed through obsolete migration plans or stale
schema examples.

**Why this priority**: This is the smallest useful cleanup because it removes
the most likely sources of contradictory agent behavior.

**Independent Test**: Review the tracked guidance and run `npx -y agnix@0.25.0 .`
plus the relevant local harness checks.

**Acceptance Scenarios**:

1. **Given** the tracked default context files, **When** an operator reviews
   AGENTS and retrieval guidance, **Then** the files point to current SDD and
   implementation-workflow sources instead of completed migration plans as
   default reading.
2. **Given** tracked custom agent TOML files, **When** the schema keys are
   inspected, **Then** Codex-facing instruction text uses
   `developer_instructions`.

### User Story 2 - Current Approved Memory (Priority: P2)

An operator using approved memory receives current, advisory memory entries with
future review dates or documented archive treatment.

**Why this priority**: Approved memory is less authoritative than runbooks, but
stale review dates erode trust in the context pack.

**Independent Test**: Inspect `.codex/memory/approved/*.md` and verify no
approved entry keeps a past `review_after` date.

**Acceptance Scenarios**:

1. **Given** approved memory entries, **When** their front matter is reviewed,
   **Then** each useful entry has current `last_verified` and future
   `review_after` values.
2. **Given** an approved memory entry that is no longer useful, **When** an
   archive pattern exists or is created, **Then** it is moved out of approved
   memory with a minimal documented archive path.

## Requirements *(mandatory)*

- **FR-001**: The implementation MUST preserve the generated Spec Kit skills
  tracked on `origin/main`.
- **FR-002**: The implementation MUST NOT add untracked legacy homelab skills
  from the main checkout.
- **FR-003**: Tracked `.codex/agents/*.toml` files MUST use
  `developer_instructions` for Codex developer instruction content.
- **FR-004**: Approved memory entries MUST NOT retain `review_after` dates before
  2026-07-03.
- **FR-005**: Default context guidance MUST NOT require operators to read
  completed migration planning documents unless those documents remain current
  operational inputs.
- **FR-006**: Evidence MUST record workflow validation, local checks,
  documentation impact, development-smoke exception, final branch, final `HEAD`,
  and verifier handoff status.

## Risk And Validation Expectations

This implementation is `low` risk and maps to workflow tier `docs-only` because
it changes documentation and local agent configuration only. Run relevant local
checks and broad repository pre-commit validation. No development-cluster smoke
is required because no cluster desired state, application behavior, or operator
command path changes.

## Success Criteria *(mandatory)*

- **SC-001**: `git ls-files` for the scoped paths shows only generated Spec Kit
  skills under tracked `.agents/skills/`.
- **SC-002**: All tracked `.codex/agents/*.toml` files use the current Codex
  schema key for developer instruction content.
- **SC-003**: All tracked approved memory entries have `review_after` dates on
  or after 2026-07-03, or are archived with a documented archive path.
- **SC-004**: Expected local validation commands are recorded with pass, fail, or
  documented skip outcomes in `specs/sdd-skill-doc-cleanup/evidence.md`.

## Assumptions

- The current date for review metadata is 2026-07-03.
- The implementation owner may perform tracked edits because the user explicitly
  designated this agent as `implementation-agent-sdd-skill-doc-cleanup`.
- The documentation cleanup does not affect generated architecture, so
  `docs/architecture.md` should remain unchanged.

## Open Questions

- None.
