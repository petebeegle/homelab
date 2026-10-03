# Plan: Repair Gateway API update documentation

- SDD tier: low; workflow risk tier: docs-only for this repair.
- Original dependency update: high risk; this repair does not establish runtime
  compatibility or replace development rollout validation of that upgrade.
- Spec, plan, and task approval: user's "fix them fan out" instruction follows
  the review describing the exact generated-doc correction.
- Smoke strategy: `none` for generated-document-only changes; renderer and
  pre-commit checks prove this repair. No production changes.
- Fanout targets: owner handles #378; helpers handle #376, #377, and #383 in
  separate worktrees and separate implementation artifacts.

## Approach

1. Capture the existing architecture check failure.
2. Bootstrap the four durable Spec Kit artifacts before implementation.
3. Run the architecture renderer, inspect the diff, then run checks.
4. Record evidence, commit, and fast-forward the existing PR branch.

## Constitution Check And Exceptions

Desired state stays in Git; no secrets or cluster resources change. A lightweight
SDD exception applies to this mechanical generated-doc repair: clarify and
standalone checklist/analyze/converge workflows are replaced by direct scope,
requirements, and diff review recorded in evidence.

The preferred `/workspaces/homelab-worktrees` location was unwritable; use
`/home/vscode/homelab-worktrees/repair-renovate-gateway`. The local branch follows
`codex/<implementation>`; its reviewed commit updates the existing Renovate PR
branch to honor the user's repair request without creating another PR.

## Validation

Use the existing renderer as the failure and success check. No new tests are
needed for deterministic generated documentation. Run relevant pre-commit hooks
and Spec Kit artifact validation before push; observe GitHub CI afterward.
