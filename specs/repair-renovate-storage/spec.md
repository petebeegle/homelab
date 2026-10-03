# Specification: Repair Renovate storage documentation

**Branch**: `codex/repair-renovate-storage`
**Date**: 2026-10-03
**SDD tier**: low

## Intent and approval

The user instructed “fix them fan out” after review identified PR #383's stale
generated architecture document. This approval covers the clear, low-risk spec,
plan, and task gates for this previously reviewed repair.

## Binding sources

- `AGENTS.md`
- `.specify/memory/constitution.md`
- `docs/runbooks/spec-driven-development.md`
- `docs/runbooks/implementation-workflow.md`
- `docs/decisions/tdd-and-development-smoke-evidence.md`

## Requirements and acceptance

- FR-001: Regenerate `docs/architecture.md` so its local-path-provisioner source
  reference matches the PR's existing v0.0.37 dependency update.
- FR-002: Preserve all manifests and unrelated work; this repair changes only
  generated documentation and its own implementation artifacts.
- FR-003: Reproduce the failed architecture check and record passing validation
  after regeneration, with runtime validation limitations explicit.

US1: An operator reviewing PR #383 sees accurate generated architecture, and
`python3 tools/architecture/render.py --check` succeeds.

Scope excludes changing the dependency version or deploying the original upgrade.
No requirements require clarification; lightweight exceptions are in evidence.
