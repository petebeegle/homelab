---
id: ADR-0012
status: accepted
scope:
  - codex-harness
  - implementation-workflow
  - agent-operations
authority: binding
created: 2026-05-10
last_verified: 2026-05-10
supersedes: []
superseded_by:
---

# Codex Implementation Workflow

## Decision

All repository code changes must use the mandatory implementation workflow in `docs/runbooks/implementation-workflow.md`.

Implementation work must happen in a sibling clone under `/workspaces/homelab-ideas/<implementation>` on branch `codex/<implementation>`. Before tracked files change, the clone must contain both a valid `.codex/tmp/active-implementation` marker and a valid `.codex/tmp/implementation-plan.yaml` plan.

Approved memory may summarize or point to this workflow, but it is not the canonical authority for the policy.

## Rationale

- Binding workflow policy belongs in decision records and runbooks, not only in approved memory.
- A local implementation plan makes scope, documentation impact, tests, verification, and risks explicit before edits begin.
- Hook enforcement catches accidental edits in the planner checkout or on non-implementation branches.
- Exact-`HEAD` verifier approval before push and PR creation keeps review tied to the actual branch state.

## Consequences

- Code-change requests begin with planning in the main checkout and move to a sibling implementation clone for edits.
- The implementation owner owns tracked edits, commits, `.codex/tmp/active-implementation`, `.codex/tmp/implementation-plan.yaml`, `.codex/tmp/pr-summary.md`, and final branch state.
- Helper agents may research, test, verify, or prepare patch recommendations, but only the implementation owner mutates tracked files.
- Hook enforcement happens at mutating tool or tracked-file-change boundaries; natural-language request detection remains advisory.
- The approved memory entry for this workflow must remain advisory or superseded by this decision.

## Operational Notes

- Validate the active marker with `tools/codex-harness/validate_active_implementation.py`.
- Validate the local plan with `tools/codex-harness/validate_implementation_plan.py`.
- Use `docs/runbooks/implementation-workflow.md` as the step-by-step procedure.
