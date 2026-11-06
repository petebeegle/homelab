# Agent session supervisor — specification

Status: draft; human approval pending.

## Problem
Multiple independent Codex sessions are difficult to track and useful parallel work requires manual coordination. Current workflow has strong safety gates but no cross-session portfolio view.

## User outcomes
- A single read-only command summarizes implementation worktrees and their branches.
- A future supervisor can delegate bounded, independent tasks and collect evidence without weakening existing SDD, GitOps, SOPS, Terraform, or production safeguards.
- Unknown or missing state is explicitly reported, never interpreted as success.

## Acceptance criteria for first increment
1. A CLI lists local Git worktrees and their branch/HEAD, identifying codex implementations.
2. Output supports machine-readable JSON and human-readable text.
3. Detached worktrees and missing metadata do not crash the command.
4. The command never starts agents, runs kubectl, pushes commits, or mutates Git state.
5. Existing hooks, guards, approvals and deployment behavior remain unchanged.

## Non-goals
Autonomous dispatch, PR merging, production operations, lease management, event collection, or automatic changes to SDD approval policy.

## Security
Do not read or display credentials, secret manifests, tool payloads, or prompt content. Avoid inferring agent liveness from worktree existence.
