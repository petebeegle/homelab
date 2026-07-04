# Feature Specification: dev-secret-staging-for-smoke

**Feature Branch**: `codex/dev-secret-staging-for-smoke`
**Created**: 2026-07-03
**Status**: Draft
**Risk Tier**: low
**Input**: User description: "Fix the dev smoke blocker: staged development Terraform vars/secrets were missing, so live branch smoke keeps stopping before Flux activation."

## Summary

Make development smoke preparation reliable by providing one repo-local command
that stages `terraform/development/terraform.tfvars` from the planner checkout
and installs it into implementation or verifier clones before live branch smoke
commands run.

## Binding Sources

- `AGENTS.md`
- `.specify/memory/constitution.md`
- `docs/runbooks/spec-driven-development.md`
- `docs/runbooks/implementation-workflow.md`
- `docs/runbooks/development-cluster.md`
- `docs/decisions/terraform-sensitive-values.md`
- `docs/decisions/tdd-and-development-smoke-evidence.md`

## Scope

### In Scope

- Add `.codex/scripts/prepare_development_smoke_secrets.sh`.
- Validate missing, tracked, non-ignored, single-clone, and multi-clone behavior.
- Document the wrapper as the pre-smoke setup step for development branch
  validation.

### Out Of Scope

- Running live development smoke.
- Printing, reading, decrypting, or committing secret values.
- Adding new smoke profiles or changing Kubernetes/Terraform desired state.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Prepare Smoke Inputs Reliably (Priority: P1)

As an implementation owner or verifier, I can run one safe command before live
development smoke so the required development Terraform vars exist in the clone
that runs `verify_branch_deploy.py`.

**Why this priority**: This directly addresses the blocker that stopped live
smoke before Flux branch activation.

**Independent Test**: Unit tests create temporary repos and confirm the wrapper
stages and installs only the expected ignored tfvars path.

**Acceptance Scenarios**:

1. **Given** an ignored `terraform/development/terraform.tfvars` in the planner
   checkout, **When** the wrapper runs for an implementation clone, **Then** the
   clone receives the same repo-relative file with mode `0600`.
2. **Given** two clone paths, **When** the wrapper runs, **Then** both clones
   receive the staged tfvars file.

### User Story 2 - Refuse Unsafe Secret Sources (Priority: P2)

As an operator, I need the wrapper to fail before copying anything unsafe.

**Why this priority**: The command handles local secret material and must not
normalize unsafe source paths.

**Independent Test**: Unit tests cover missing, tracked, and non-ignored
`terraform/development/terraform.tfvars`.

**Acceptance Scenarios**:

1. **Given** the development tfvars file is missing, **When** the wrapper runs,
   **Then** it exits non-zero before staging.
2. **Given** the development tfvars file is tracked or not ignored, **When** the
   wrapper runs, **Then** it exits non-zero and does not install the file.

## Requirements *(mandatory)*

- **FR-001**: The wrapper MUST default to installing into
  `/workspaces/homelab-ideas/<implementation>` when clone paths are omitted.
- **FR-002**: The wrapper MUST stage only
  `terraform/development/terraform.tfvars` for this workflow.
- **FR-003**: The wrapper MUST refuse missing, tracked, or non-ignored source
  tfvars files.
- **FR-004**: The wrapper MUST install staged tfvars into every requested clone
  with file mode `0600`.
- **FR-005**: Documentation MUST make the wrapper the standard pre-smoke step
  before `verify_branch_deploy.py --push`, `--terraform-apply`, or verifier
  reruns that need development Terraform preflight.
- **FR-006**: Evidence MUST record local tests, shell syntax checks, pre-commit,
  and the docs-only/local-tooling development smoke exception.

## Risk And Validation Expectations

This is a `low` SDD change because it adds local wrapper tooling and docs. It
does not change live cluster desired state. Focused unit tests are required.

## Success Criteria *(mandatory)*

- **SC-001**: Unit tests pass for success, missing, tracked, non-ignored, mode,
  and multi-clone scenarios.
- **SC-002**: `bash -n .codex/scripts/*.sh` passes.
- **SC-003**: `pre-commit run --all-files` passes.

## Assumptions

- The wrapper is run from the planner checkout containing local ignored
  development Terraform vars.
- Secret values are never printed; path names and counts are acceptable
  operational output.

## Open Questions

- None.
