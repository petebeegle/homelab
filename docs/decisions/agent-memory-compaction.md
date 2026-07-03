---
id: ADR-0007
status: accepted
scope:
  - agent-memory
  - context-management
authority: binding
created: 2026-05-09
last_verified: 2026-07-03
supersedes: []
superseded_by:
---

# Agent Memory And Compaction

## Decision

Use explicit context summaries or compaction at stable task boundaries, not during the middle of implementation.

## Rationale

- Mid-task compaction can lose exact file paths, variable names, and command outputs.
- Boundary summaries preserve intent while reducing stale or irrelevant context.
- Clearing context between unrelated tasks avoids carrying false assumptions.

## Consequences

- Compact after research, debugging, or a completed milestone.
- Avoid compaction while editing or before verification is complete.
- When resuming, reread `AGENTS.md`, `docs/runbooks/spec-driven-development.md`,
  `docs/runbooks/implementation-workflow.md`, and the relevant decision or
  runbook docs for the active task.

## Operational Notes

- Summaries should include changed paths, decisions made, commands run, and unresolved risks.
- Prefer a full context clear between unrelated workstreams.
- Treat repo docs as shared memory and keep them agent-neutral.
