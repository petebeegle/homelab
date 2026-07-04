---
status: current
scope:
  - codex-harness
  - implementation-workflow
authority: reference
created: 2026-05-12
last_verified: 2026-07-03
---

# Codex Workflow Protocol Reference

This reference records local machine-readable signals used by
`docs/runbooks/implementation-workflow.md`.

## Prompt Intent Marker

The `UserPromptSubmit` hook may write `.codex/tmp/repo-change-intent` when a
prompt appears to request repository changes. This marker is advisory and exists
to surface workflow reminders before tracked files change.

The reminder tells agents that the default execution mode is a worktree:

```bash
git fetch origin
git worktree add /workspaces/homelab-worktrees/<implementation> \
  -b codex/<implementation> origin/main
```

Mutation, push, and PR guards remain the authoritative enforcement points.

## Durable Spec Kit Evidence

Durable workflow state lives under `specs/<implementation>/`:

- `spec.md`
- `plan.md`
- `tasks.md`
- `evidence.md`

Push and PR automation require these files to be present and non-empty on the
matching branch `codex/<implementation>`.
