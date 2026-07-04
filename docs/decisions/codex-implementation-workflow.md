---
id: ADR-0012
status: accepted
scope:
  - codex-harness
  - implementation-workflow
  - agent-operations
authority: binding
created: 2026-05-10
last_verified: 2026-07-03
supersedes: []
superseded_by:
---

# Codex Implementation Workflow

## Decision

All repository code changes must use the Spec Kit implementation workflow in
`docs/runbooks/implementation-workflow.md`.

Implementation work is isolated by branch and durable Spec Kit artifacts. Each
implementation uses branch `codex/<implementation>`, directory
`specs/<implementation>/`, and one PR. Tracked edits on `main` or on non-Codex
implementation branches are rejected by local guards.

The default local execution mode is a dedicated worktree under
`/workspaces/homelab-worktrees/<implementation>`. Users may explicitly request
the current checkout or a sibling clone when appropriate.

Before push or automatic PR creation, `specs/<implementation>/spec.md`,
`plan.md`, `tasks.md`, and `evidence.md` must be present and non-empty. If
`evidence.md` records an explicit final, verified, approved, branch, or current
`HEAD`, that SHA must match the current branch `HEAD`.

Local owner attestations, verifier attestations, delegation tokens, and
exact-`HEAD` verifier approval files are no longer required. Review gating is
provided by normal GitHub PR review and status checks.

## Rationale

- Spec Kit now provides the standard implementation lifecycle and artifact
  structure.
- Worktrees keep concurrent efforts isolated without requiring local
  attestation files.
- Branch and SDD artifact guards catch accidental tracked edits on `main` or on
  mismatched branches.
- PR review and status checks are the durable review mechanism.

## Consequences

- Repo-changing prompts default to worktree setup guidance.
- Sibling clones remain allowed, but are no longer required.
- `.codex/tmp/` stays local scratch and must not contain durable requirements or
  evidence.
- Existing historical validators for old attestation files are not part of the
  current workflow contract.

## Operational Notes

- Use `docs/runbooks/implementation-workflow.md` as the step-by-step procedure.
- Validate durable Spec Kit context with
  `tools/codex-harness/validate_sdd_context.py`.
- Keep useful evidence in `specs/<implementation>/evidence.md`.
