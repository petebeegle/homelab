---
status: approved
created: 2026-05-09
last_verified: 2026-05-16
review_after: 2026-08-16
source: user-preference
kind: workflow-preference
scope:
  - implementation-workflow
  - codex-harness
authority: advisory
supersedes: []
superseded_by:
  - docs/decisions/codex-implementation-workflow.md
---

# Mandatory Implementation Workflow

This memory is an advisory pointer only. The binding implementation workflow authority is `docs/decisions/codex-implementation-workflow.md`, and the canonical procedure is `docs/runbooks/implementation-workflow.md`.

High-level memory: repository code changes are planned and coordinated by the main agent, while tracked implementation and exact-`HEAD` verification are delegated to separate implementation and verifier subagents when runtime tooling permits. See the ADR and runbook for required markers, attestations, validation, PR summary, verifier approval, and PR creation details.
