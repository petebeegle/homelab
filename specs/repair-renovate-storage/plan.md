# Plan: Repair Renovate storage documentation

**Branch**: `codex/repair-renovate-storage`
**SDD tier**: low
**Workflow risk tier**: docs-only
**Smoke strategy**: none; the repair changes generated documentation only.
**Development validation**: none for this repair; the original controller
upgrade remains runtime-unverified by this work.

## Approach and gates

The user's “fix them fan out” instruction approves the reviewed repair's spec,
plan, and tasks together under the lightweight workflow exception. Bootstrap
artifacts before implementation, reproduce `render.py --check`, regenerate using
`render.py --write`, inspect the exact generated diff, and run the relevant
pre-commit hooks plus the SDD context validator and whitespace check. No new tests
are needed for generated documentation; the existing failing validator is the
regression check.

## Fanout and ownership

This lane owns `docs/architecture.md` and `specs/repair-renovate-storage/` in
`/home/vscode/homelab-worktrees/repair-renovate-storage`. Other lanes repair other
PRs independently. All this lane's evidence is consolidated in `evidence.md`.
The parent handles push and PR review after a local conventional commit.

## Invariants and exceptions

Git remains the source of truth. No live state, manifests, secrets, ingress,
storage configuration, or Talos operations change. Constitution invariants are
preserved. The writable worktree path substitutes for the unavailable default
`/workspaces/homelab-worktrees` location. The local codex branch will update the
existing Renovate PR branch, an intentional exception to creating a new PR.
Clarify, checklist, analyze, and converge are lightweight exceptions documented
in evidence; requirements and actual diff are reconciled directly.

## Documentation impact

Only the generated local-path-provisioner version row should change. A wider
generated diff must be investigated before committing.
