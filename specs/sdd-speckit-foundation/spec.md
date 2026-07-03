# Feature Specification: sdd-speckit-foundation

**Feature Branch**: `codex/sdd-speckit-foundation`
**Created**: 2026-07-03
**Status**: Implemented
**Risk Tier**: low
**Workflow Tier**: docs-only
**Input**: Initialize Spec Kit scaffolding and Homelab SDD guidance for the first
PR in the mandatory workflow.

## Summary

Homelab contributors need a durable Spec Kit foundation that captures
requirements, plans, tasks, and evidence for each implementation while keeping
the existing ADRs, runbooks, GitOps workflow, and verifier model authoritative.

## Binding Sources

- `AGENTS.md`
- `.specify/memory/constitution.md`
- `docs/runbooks/implementation-workflow.md`
- `docs/decisions/codex-implementation-workflow.md`
- `docs/decisions/flux-gitops-source-of-truth.md`
- `docs/decisions/cilium-gateway-api-ingress.md`
- `docs/decisions/sops-age-secrets.md`
- `docs/decisions/synology-nfs-storage.md`
- `docs/decisions/talos-management-boundaries.md`
- `docs/decisions/tdd-and-development-smoke-evidence.md`

## Scope

### In Scope

- Initialize actual Spec Kit scaffolding with the Codex integration when
  available.
- Add a Homelab constitution that summarizes binding rules and links to their
  canonical sources.
- Add custom SDD templates and artifact guidance for `spec.md`, `plan.md`,
  `tasks.md`, and `evidence.md`.
- Add an SDD runbook covering Spec Kit version checks, tiered workflow, artifact
  ownership, spec persistence, and `.codex/tmp` scratch behavior.
- Shorten `AGENTS.md` into a router for SDD, canonical runbooks, and binding
  ADRs without losing critical invariants.
- Add foundation artifacts for this implementation under
  `specs/sdd-speckit-foundation/`.

### Out Of Scope

- Hook or validator enforcement for specs.
- Push guard changes.
- Skills cleanup.
- Development smoke matrix expansion.
- Removing untracked local files in the main checkout.
- Verifier approval or PR creation by the implementation owner.

## User Scenarios & Testing

### User Story 1 - Start SDD Work Reliably (Priority: P1)

As an implementation owner, I can find the SDD entrypoint, create durable spec
artifacts, and understand how they relate to the mandatory workflow before
editing tracked files.

**Why this priority**: The first SDD PR must make future implementation starts
clear and repeatable.

**Independent Test**: Review `AGENTS.md`,
`docs/runbooks/spec-driven-development.md`, `.specify/memory/constitution.md`,
and the templates to confirm they route to the workflow and binding ADRs.

**Acceptance Scenarios**:

1. **Given** a new implementation, **When** an owner reads `AGENTS.md`, **Then**
   they can identify the SDD runbook, implementation workflow, and required
   spec directory.
2. **Given** an SDD artifact conflicts with an ADR, **When** an owner reads the
   constitution, **Then** they know the ADR remains binding and the SDD artifact
   must be updated.

### User Story 2 - Preserve Homelab Operational Rules (Priority: P2)

As a reviewer, I can verify that the Spec Kit foundation captures the Homelab
rules for GitOps, Gateway API, SOPS, NFS, Talos, development validation,
documentation impact, sibling-clone ownership, verifier approval, and no
production-first mutation.

**Why this priority**: SDD must not dilute the operational safety rules already
accepted by ADRs and runbooks.

**Independent Test**: Check `.specify/memory/constitution.md`,
`.specify/templates/plan-template.md`, and this spec for the listed invariants
and canonical links.

**Acceptance Scenarios**:

1. **Given** a future Kubernetes change, **When** the owner fills out
   `plan.md`, **Then** development validation and Gateway/SOPS/NFS checks are
   prompted before implementation handoff.
2. **Given** a future docs-only change, **When** the owner fills out
   `evidence.md`, **Then** they can record why live development smoke is not
   required and which substitute checks ran.

### User Story 3 - Capture Evidence Durably (Priority: P3)

As a verifier, I can inspect committed evidence for command outcomes, Spec Kit
initialization, exceptions, documentation impact, and final branch state without
depending on ignored `.codex/tmp` files.

**Why this priority**: Verifier review needs stable context after local scratch
files are gone.

**Independent Test**: Review `specs/sdd-speckit-foundation/evidence.md` and
`.specify/templates/evidence-template.md`.

**Acceptance Scenarios**:

1. **Given** commands ran during implementation, **When** a verifier opens
   `evidence.md`, **Then** each requested command has a pass, fail, or skipped
   outcome with notes.
2. **Given** `.codex/tmp` remains ignored, **When** the branch is pushed, **Then**
   durable evidence still exists under `specs/<implementation>/`.

## Requirements

- **FR-001**: The repository MUST include Spec Kit scaffolding initialized with
  Codex integration, or document a generic integration fallback if Codex is not
  available.
- **FR-002**: The Homelab constitution MUST summarize and link the current
  binding rules for GitOps, Gateway API, SOPS, NFS, Talos, development
  validation, documentation impact, sibling-clone ownership, verifier approval,
  and no production-first mutation.
- **FR-003**: SDD templates MUST guide authors to create `spec.md`, `plan.md`,
  `tasks.md`, and `evidence.md` artifacts with tiered tiny, low, medium, and
  high expectations.
- **FR-004**: The SDD runbook MUST explain Spec Kit version/upgrade checks,
  tiered workflow, artifact ownership, spec persistence, and `.codex/tmp`
  scratch behavior.
- **FR-005**: `AGENTS.md` MUST become a shorter router to SDD, canonical
  runbooks, and ADRs while preserving critical repo invariants.
- **FR-006**: This implementation MUST include `spec.md`, `plan.md`, `tasks.md`,
  and `evidence.md` under `specs/sdd-speckit-foundation/`.
- **FR-007**: Evidence MUST record all requested command outcomes and any
  exceptions.

## Risk And Validation Expectations

This implementation is SDD `low` because it changes agent guidance, templates,
and runbooks, and workflow `docs-only` because it does not change executable
repo behavior, Kubernetes desired state, Terraform, Flux wiring, Gateway routes,
storage, or secrets.

No development-cluster smoke is required. Substitute checks are local workflow
validators, architecture check, unit tests, pre-commit, agent-memory pytest, and
smoke test npm suite where feasible.

## Success Criteria

- **SC-001**: `uvx --from git+https://github.com/github/spec-kit.git specify
  init --here --force --integration codex` succeeds, or fallback is documented.
- **SC-002**: Workflow marker, plan, and owner attestation validators pass before
  tracked edits.
- **SC-003**: Requested local checks are run where feasible and recorded in
  `evidence.md` and `.codex/tmp/pr-summary.md`.
- **SC-004**: Final branch contains a conventional commit and no verifier
  approval files.

## Assumptions

- Spec Kit templates may be customized for Homelab as long as generated
  integration metadata remains intact.
- `.codex/tmp` remains ignored and should not be used for durable requirements
  or evidence.
- Documentation and SDD scaffolding changes do not require development-cluster
  smoke unless they alter executable app or cluster behavior.

## Open Questions

- None.
