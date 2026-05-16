---
status: current
scope:
  - codex-harness
  - implementation-workflow
authority: binding
created: 2026-05-10
last_verified: 2026-05-16
---

# Implementation Workflow

Use this runbook for every repository code change. The binding decision is `docs/decisions/codex-implementation-workflow.md`.

## Procedure

1. Plan in the main checkout at `/workspaces/homelab`; do not edit tracked files there.
2. Choose a single implementation name. One implementation maps to one pull request and branch `codex/<implementation>`.
3. If ignored local secrets or configs are required, stage them under `.codex/tmp/implementation-secrets/<implementation>/` in the main checkout, preserving repo-relative paths and never logging contents.
4. Clone the repo into `/workspaces/homelab-ideas/<implementation>` and create `codex/<implementation>` from `origin/main`.
5. Before tracked edits, create `.codex/tmp/active-implementation` with `implementation`, `branch`, `base`, `role`, `clone_path`, `owner_role`, and `owner_agent`.
6. Before tracked edits, create `.codex/tmp/implementation-plan.yaml` with implementation identity, summary, scope, out-of-scope items, planned changes, documentation impact, tests, verification, and risks. Tests, verification, and risks must declare the risk-tiered TDD and development smoke expectations for the implementation, or explain why they do not apply.
7. Before tracked edits, create `.codex/tmp/implementation-owner-attestation.yaml` with implementation identity, role, concrete `agent_id`, clone path, `created_at`, and matching delegation token evidence under `.codex/tmp/delegation-tokens/`.
8. Validate the marker, plan, and owner attestation.
9. Make tracked-file changes only in the sibling clone.
10. Update docs, generated docs, decision records, runbooks, or agent guidance when behavior changes. If no docs change, record why in `.codex/tmp/pr-summary.md`.
11. Commit with conventional commits.
12. Run relevant checks, collect TDD and development smoke evidence expected by the plan, and request verifier review.
13. Record verifier approval for the exact `HEAD` SHA in `.codex/tmp/verifier-approved`.
14. Record `.codex/tmp/verifier-attestation.yaml` with verifier identity, separate delegation token evidence, and `approved_head` equal to the exact `HEAD` SHA. The verifier `agent_id`, `delegation_token`, and `delegation_token_path` must differ from the implementation owner evidence.
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
owner_agent=implementation-agent-<implementation>
```

`owner_agent` must be a concrete implementation owner identity with the `implementation-agent-` prefix. Generic role labels such as `codex`, `assistant`, `planner`, `parent`, `main`, `self`, and `orchestrator` are rejected.

## Implementation Plan

```yaml
implementation: <implementation>
branch: codex/<implementation>
base: origin/main
clone_path: /workspaces/homelab-ideas/<implementation>
owner_agent: implementation-agent-<implementation>
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
agent_id: implementation-agent-<implementation>
clone_path: /workspaces/homelab-ideas/<implementation>
created_at: <UTC timestamp>
delegation_token: implementation-delegation-<implementation>
delegation_token_path: .codex/tmp/delegation-tokens/implementation-agent-<implementation>.token
```

`agent_id` must match the active marker `owner_agent` and the implementation plan `owner_agent`.

The referenced delegation token file must be repo-relative, live under `.codex/tmp/delegation-tokens/`, and contain matching `delegation_token`, `implementation`, `role`, `agent_id`, and `created_at` fields.

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
agent_id: verifier-agent-<implementation>
clone_path: /workspaces/homelab-ideas/<implementation>
created_at: <UTC timestamp>
approved_head: <exact HEAD SHA>
delegation_token: verifier-delegation-<implementation>
delegation_token_path: .codex/tmp/delegation-tokens/verifier-agent-<implementation>.token
```

The verifier `agent_id` must be concrete, must use the `verifier-agent-` prefix, must not use a generic role label, and must differ from the implementation owner `agent_id`. The verifier delegation token and token path must also differ from the implementation owner evidence.

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

## Risk-Tiered TDD And Smoke Evidence

TDD and development smoke evidence is advisory in v1. It is still expected for normal work, but it is documented and reviewed rather than enforced by hard harness gates. See `docs/decisions/tdd-and-development-smoke-evidence.md`.

Declare a risk tier in the plan:

- `docs-only`: documentation, generated docs, decisions, runbooks, or agent guidance only.
- `low`: narrow code or manifest changes with local-only behavior and low operational blast radius.
- `medium`: app behavior, Kubernetes manifests, Flux wiring, Terraform module logic, storage, secrets references, or Gateway routes.
- `high`: cluster-scoped controllers, CRDs, networking, storage classes, authentication, production traffic paths, secret handling, or changes that can affect multiple apps.

TDD expectations by tier:

- `docs-only`: no code TDD required; run relevant doc, harness, or repo tests that guard the edited guidance when available.
- `low`: add or update the smallest unit test that fails before the fix when the codebase has a reasonable test seam; otherwise document the exception.
- `medium`: prefer a red-green flow for behavior changes, including local render tests or focused unit tests for Kubernetes/Terraform tooling where applicable.
- `high`: use a test-helper lane by default to identify or prepare failing tests before implementation, plus broader verification after the change. If no useful failing test can be made, record why.

Development smoke expectations by tier:

- `docs-only`: no live development smoke required.
- `low`: smoke only when the changed path affects live app rendering or operator commands.
- `medium`: use a smoke-helper lane by default for touched apps or explain why local verification is enough.
- `high`: run development cluster smoke for the affected app or base path when credentials and cluster health allow it; otherwise record the blocker and the safest substitute evidence.

## Helper Lanes

Use helper lanes without breaking the single-owner model:

- `test-helper`: researches risk, proposes or runs failing tests, and reports command output or patch recommendations. The implementation owner remains the only role that applies tracked-file edits.
- `smoke-helper`: prepares or runs development cluster smoke checks, captures exact branch and `HEAD` evidence, and recommends cleanup. The implementation owner remains responsible for final branch state and PR notes.

Helper output belongs in `.codex/tmp/pr-summary.md` or an equivalent local note when it affects verifier review. Include commands, outcomes, skipped checks, and exceptions. Do not create verifier approval files from helper lanes.

## Evidence Audit

Before requesting verifier review, the implementation owner should audit:

- The plan declares the intended TDD and smoke expectations for the risk tier.
- Any skipped failing test, missing smoke profile, unavailable development cluster, or other exception is recorded with a reason.
- Test evidence includes the exact commands run and pass/fail result.
- Development smoke evidence includes app name, branch, branch slug, exact `HEAD`, smoke profile or documented exception, report path if one was produced, cleanup status, and whether stale reports were ignored or removed.
- Parent/process evidence is internally consistent: active marker, plan, owner attestation, delegation token, branch, clone path, and PR summary all point at the same implementation.

Verifier review should audit the same evidence. If declared TDD or smoke evidence is stale, missing, or inconsistent with the risk tier, the verifier should request a rerun, run a spot check, or record the residual risk before sign-off.
