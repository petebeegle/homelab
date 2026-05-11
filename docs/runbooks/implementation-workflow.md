---
status: current
scope:
  - codex-harness
  - implementation-workflow
authority: binding
created: 2026-05-10
last_verified: 2026-05-11
---

# Implementation Workflow

Use this runbook for every repository code change. The binding decision is `docs/decisions/codex-implementation-workflow.md`.

## Procedure

1. Plan in the main checkout at `/workspaces/homelab`; do not edit tracked files there.
2. Choose a single implementation name. One implementation maps to one pull request and branch `codex/<implementation>`.
3. If ignored local secrets or configs are required, stage them under `.codex/tmp/implementation-secrets/<implementation>/` in the main checkout, preserving repo-relative paths and never logging contents.
4. Clone the repo into `/workspaces/homelab-ideas/<implementation>` and create `codex/<implementation>` from `origin/main`.
5. Before tracked edits, create `.codex/tmp/active-implementation` with `implementation`, `branch`, `base`, `role`, `clone_path`, `owner_role`, and `owner_agent`.
6. Before tracked edits, create `.codex/tmp/implementation-plan.yaml` with implementation identity, summary, scope, out-of-scope items, planned changes, documentation impact, tests, verification, and risks.
7. Before tracked edits, create `.codex/tmp/implementation-owner-attestation.yaml` with implementation identity, role, concrete `agent_id`, clone path, and `created_at`.
8. Validate the marker, plan, and owner attestation.
9. Make tracked-file changes only in the sibling clone.
10. Update docs, generated docs, decision records, runbooks, or agent guidance when behavior changes. If no docs change, record why in `.codex/tmp/pr-summary.md`.
11. Commit with conventional commits.
12. Run relevant checks and request verifier review.
13. Record verifier approval for the exact `HEAD` SHA in `.codex/tmp/verifier-approved`.
14. Record `.codex/tmp/verifier-attestation.yaml` with verifier identity and `approved_head` equal to the exact `HEAD` SHA. The verifier `agent_id` must differ from the implementation owner `agent_id`.
15. Write `.codex/tmp/pr-summary.md` from the plan and final result.
16. Create the pull request against `main`; delete the sibling clone only after PR creation succeeds.

## Active Marker

```text
implementation=<implementation>
branch=codex/<implementation>
base=origin/main
role=implementation
clone_path=/workspaces/homelab-ideas/<implementation>
owner_role=implementation-agent
owner_agent=<implementation-owner>
```

`owner_agent` must be a concrete implementation owner identity. Generic role labels such as `codex`, `assistant`, `planner`, `parent`, `main`, `self`, and `orchestrator` are rejected.

## Implementation Plan

```yaml
implementation: <implementation>
branch: codex/<implementation>
base: origin/main
clone_path: /workspaces/homelab-ideas/<implementation>
owner_agent: <implementation-owner>
summary: <one sentence>
scope:
  - <included work>
out_of_scope:
  - <excluded work>
planned_changes:
  - <change>
docs_impact: <docs updated or why none are needed>
tests:
  - <command or scenario>
verification:
  - <review or acceptance check>
risks:
  - <known risk or none>
```

## Owner Attestation

```yaml
implementation: <implementation>
branch: codex/<implementation>
base: origin/main
role: implementation-agent
agent_id: <implementation-owner>
clone_path: /workspaces/homelab-ideas/<implementation>
created_at: <UTC timestamp>
```

`agent_id` must match the active marker `owner_agent` and the implementation plan `owner_agent`.

## Verifier Approval And Attestation

```text
<exact HEAD SHA>
```

Write the exact `HEAD` SHA to `.codex/tmp/verifier-approved`.

```yaml
implementation: <implementation>
branch: codex/<implementation>
base: origin/main
role: verifier-agent
agent_id: <verifier-agent>
clone_path: /workspaces/homelab-ideas/<implementation>
created_at: <UTC timestamp>
approved_head: <exact HEAD SHA>
```

The verifier `agent_id` must be concrete, must not use a generic role label, and must differ from the implementation owner `agent_id`.

## Validation

```bash
python3 tools/codex-harness/validate_active_implementation.py \
  --marker .codex/tmp/active-implementation \
  --root "$(pwd)" \
  --branch "$(git branch --show-current)"

python3 tools/codex-harness/validate_implementation_plan.py \
  --plan .codex/tmp/implementation-plan.yaml \
  --marker .codex/tmp/active-implementation \
  --root "$(pwd)" \
  --branch "$(git branch --show-current)"

python3 tools/codex-harness/validate_workflow_attestations.py \
  --kind owner \
  --attestation .codex/tmp/implementation-owner-attestation.yaml \
  --marker .codex/tmp/active-implementation \
  --plan .codex/tmp/implementation-plan.yaml \
  --root "$(pwd)" \
  --branch "$(git branch --show-current)"

python3 tools/codex-harness/validate_workflow_attestations.py \
  --kind verifier \
  --attestation .codex/tmp/verifier-attestation.yaml \
  --marker .codex/tmp/active-implementation \
  --owner-attestation .codex/tmp/implementation-owner-attestation.yaml \
  --head "$(git rev-parse HEAD)" \
  --root "$(pwd)" \
  --branch "$(git branch --show-current)"
```

## Ownership

Use implementation and verifier subagents by default whenever runtime tooling exposes them. Self-implementation or self-verification is acceptable only when subagent tooling is unavailable or higher-priority runtime policy blocks delegation, and the fallback must be recorded in `.codex/tmp/pr-summary.md`.

Multiple helpers may contribute through the single integrator model. Helpers may inspect, test, verify, or recommend patches, but one implementation owner applies tracked-file edits and owns final branch state.
