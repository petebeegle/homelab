# Feature Specification: Repair Gateway API update documentation

**Feature Branch**: `codex/repair-renovate-gateway`
**Created**: 2026-10-03
**Status**: Approved for bounded repair
**Risk Tier**: low

## Human Gate Status

The review identified stale generated architecture documentation as the only CI
failure in PR #378. The user then instructed "fix them fan out", approving this
specific repair. Clarification is unnecessary because the expected output is
defined by the existing renderer.

## Summary

Restore a passing architecture documentation check for the existing Gateway API
update PR while preserving its dependency changes and unrelated work.

## Binding Sources

- `AGENTS.md`
- `.specify/memory/constitution.md`
- `docs/runbooks/spec-driven-development.md`
- `docs/runbooks/implementation-workflow.md`
- `docs/decisions/tdd-and-development-smoke-evidence.md`

## Scope

Regenerate `docs/architecture.md` and record repair evidence on PR #378. Changing
Gateway API versions, live cluster state, or unrelated Renovate policy is outside
this documentation repair.

## User Scenarios And Acceptance

Given the existing dependency update, when CI checks the architecture document,
the generated document matches repository sources and the check passes.

## Requirements

- FR-001: Generated architecture must match the updated Gateway API source URLs.
- FR-002: Preserve the PR's Kubernetes and Terraform source changes.
- FR-003: Record checks and distinguish the documentation repair from runtime
  validation of the original dependency upgrade.

## Success Criteria

The architecture check and relevant pre-commit checks pass; the repair is pushed
as a fast-forward update to the existing PR with no unrelated tracked changes.

## Assumptions And Open Questions

The user wants the existing PR repaired, not a replacement PR. No open questions.
