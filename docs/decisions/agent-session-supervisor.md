---
status: proposed
scope:
  - codex-harness
  - agent-operations
authority: advisory
created: 2026-11-06
last_verified: 2026-11-06
---

# Proposed: Supervisor-driven agent coordination

## Context
Existing Codex guardrails enforce a safe per-implementation lifecycle. They do not provide a single view of multiple active sessions or a bounded delegation model. A worktree/branch is an implementation workspace, **not proof of a live agent**.

## Decision proposed
Adopt a deterministic, read-only supervisor inventory first. Evolve toward a supervisor that owns a queue of outcomes and dispatches bounded tasks to independent worktrees, while keeping one implementation / one branch / one PR and a single evidence owner per implementation.

## Authority boundaries
- The supervisor may inspect repository state and recommend task assignments.
- Worker agents must respect existing branch guards, SOPS protection, Terraform plan gates, and GitOps-first operation.
- No automatic production mutation, merge, privilege escalation, or shared-cluster write access is granted.
- High-risk changes still require explicit human review and development validation.
- The supervisor must never equate a stopped process, absent heartbeat, or worktree with verified completion.
- No change to ADR-0012 or binding workflow policy occurs in this first increment.

## Delegation contract (future)
Every task declares implementation, expected outcome, read/write scope, dependencies, validation, and escalation triggers. A worker returns evidence and changed files, not merely a natural-language success claim. Shared mutable resources require leases before dispatch.

## Rollout
1. Read-only inventory and tests.
2. Unique session identity and event journal with safe redaction and unknown/stale state.
3. Manual bounded delegation with a single integration/review queue.
4. Measured experiments; only then consider automatic dispatch or approval-policy changes.

## Rejected for now
Always-on Kubernetes-hosted orchestration, broad MCP write access, and automatic PR merges.
