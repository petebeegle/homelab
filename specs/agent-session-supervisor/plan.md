# Plan — agent session supervisor

Status: proposed; approval pending.

- SDD tier: low (local read-only tooling plus documentation).
- Workflow risk: low; no cluster-affecting changes.
- Branch: codex/agent-session-supervisor.
- Smoke profile: none — read-only local Git introspection, no deployment.
- Architecture: start with a deterministic worktree inventory. Later add per-session lifecycle events, GitHub PR projection, and a supervisor that delegates bounded work.
- Verification: Python unit tests with mocked git output; manual `git worktree list --porcelain` comparison.
- Fanout: read-only review of session lifecycle, security model, and CLI behavior can happen independently; no simultaneous tracked edits required for this increment.
- Risks: a worktree is not a running agent; detached HEADs; stale paths; unreliable status inference.
- Exceptions: no dev-cluster smoke because this increment has no cluster effect.
- Human gates: design selection provided by requester; spec/plan/task approval not separately asserted. Keep PR draft until reviewed.

## Future supervisor design
The supervisor is a long-lived *logical role*, not necessarily a daemon. It owns a portfolio queue, assigns independent outcomes to isolated worktrees, checks dependencies and resource claims, collects evidence, and surfaces only decisions requiring human judgment. Worker agents never inherit unrestricted production credentials. Initial dispatch is manual/explicit; no autonomous spawning in this PR.

## Next increments
1. Session IDs, append-only lifecycle event journal, stale/unknown semantics and dashboard.
2. Approval policy ADR revision and testable gate changes (separate PR).
3. Bounded delegation, worktree/resource ownership, development-cluster lease, integration queue.
