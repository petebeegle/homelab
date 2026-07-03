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
6. Before tracked edits, create `.codex/tmp/implementation-plan.yaml` with implementation identity, summary, scope, out-of-scope items, planned changes, documentation impact, tests, verification, and risks. Tests, verification, and risks must declare the risk-tiered TDD and development validation expectations for the implementation, or explain why they do not apply.
7. Before tracked edits, create `.codex/tmp/implementation-owner-attestation.yaml` with implementation identity, role, concrete `agent_id`, clone path, `created_at`, and matching delegation token evidence under `.codex/tmp/delegation-tokens/`.
8. Validate the marker, plan, and owner attestation.
9. Create durable SDD artifacts under `specs/<implementation>/`: `spec.md`, `plan.md`, `tasks.md`, and `evidence.md`.
10. Make tracked-file changes only in the sibling clone.
11. Update docs, generated docs, decision records, runbooks, or agent guidance when behavior changes. If no docs change, record why in `.codex/tmp/pr-summary.md`.
12. Commit with conventional commits.
13. Run relevant checks, collect TDD evidence, and collect required development-cluster validation evidence for covered cluster-affecting changes before requesting verifier review.
14. Record command outcomes, development validation evidence or exceptions, final `HEAD`, and documentation impact in `specs/<implementation>/evidence.md`.
15. Record verifier approval for the exact `HEAD` SHA in `.codex/tmp/verifier-approved`.
16. Record `.codex/tmp/verifier-attestation.yaml` with verifier identity, separate delegation token evidence, and `approved_head` equal to the exact `HEAD` SHA. The verifier `agent_id`, `delegation_token`, and `delegation_token_path` must differ from the implementation owner evidence.
17. Write `.codex/tmp/pr-summary.md` from the plan and final result.
18. Create the pull request against `main`; delete the sibling clone only after PR creation succeeds.

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

python3 tools/codex-harness/validate_sdd_context.py \
  --marker .codex/tmp/active-implementation \
  --root "$(pwd)" \
  --branch "$(git branch --show-current)" \
  --require-plan-artifacts

python3 tools/codex-harness/validate_workflow_attestations.py \
  --kind verifier \
  --attestation .codex/tmp/verifier-attestation.yaml \
  --marker .codex/tmp/active-implementation \
  --owner-attestation .codex/tmp/implementation-owner-attestation.yaml \
  --head "$(git rev-parse HEAD)" \
  --root "$(pwd)" \
  --branch "$(git branch --show-current)"

python3 tools/codex-harness/validate_sdd_context.py \
  --marker .codex/tmp/active-implementation \
  --root "$(pwd)" \
  --branch "$(git branch --show-current)" \
  --require-plan-artifacts \
  --require-evidence \
  --head "$(git rev-parse HEAD)"
```

## SDD Guard Gates

For non-bootstrap tracked edits, the workflow guard requires valid branch,
clone, marker, implementation plan, owner attestation, delegation token, and
non-empty `specs/<implementation>/spec.md`, `plan.md`, and `tasks.md`.
Bootstrap edits that create the initial SDD artifact files are allowed only when
the branch `HEAD` does not already contain SDD artifacts for the implementation.

Verifier approval, verifier attestation, automatic PR creation, final handoff,
and non-smoke pushes require `specs/<implementation>/evidence.md` to exist and
be non-empty. When `evidence.md` records an explicit final, verified, approved,
branch, or current `HEAD`, that SHA must match the current branch `HEAD`.

`.codex/scripts/create_implementation_pr.sh --auto` performs its own marker,
plan, owner attestation, SDD evidence, verifier approval, and verifier
attestation gates before pushing or creating a PR. Do not rely on Stop-hook
ordering as the PR creation safety boundary.

Development validation may push `origin HEAD:refs/heads/codex/<implementation>`
before verifier approval only from the active implementation branch, only when
the implementation clone has valid runtime workflow context and non-empty
`spec.md`, `plan.md`, and `tasks.md`. PR creation, final handoff, and all other
origin pushes still require exact-HEAD verifier approval and verifier
attestation.

## Ownership

The main agent remains planner and orchestrator only. It may inspect repository state, stage required ignored local config for delegation, and coordinate agents, but it does not own tracked-file edits, commits, verifier approval, or final branch state.

One implementation owner subagent owns tracked-file edits, commits, `.codex/tmp/active-implementation`, `.codex/tmp/implementation-plan.yaml`, `.codex/tmp/implementation-owner-attestation.yaml`, `.codex/tmp/pr-summary.md`, and final branch state for the implementation clone.

One separate verifier subagent reviews the exact `HEAD` and owns `.codex/tmp/verifier-approved` plus `.codex/tmp/verifier-attestation.yaml`. The verifier identity and delegation token evidence must differ from the implementation owner evidence.

Helper subagents may research, test, run smoke checks, or recommend patches through the single integrator model. Helpers must not make tracked-file edits; the implementation owner applies any accepted recommendations.

If subagent tooling is unavailable or higher-priority runtime policy blocks delegation, blocked delegation is not automatic permission for main-agent self-work. The user must explicitly consent to self-implementation or self-verification for that task, and the approved fallback must be recorded in `.codex/tmp/pr-summary.md`.

## Risk-Tiered TDD And Development Validation

TDD evidence remains risk-tiered and documented. Development-cluster validation is required for covered cluster-affecting changes before production-oriented PR completion, but it is enforced by implementation and verifier review rather than hard harness gates. See `docs/decisions/tdd-and-development-smoke-evidence.md`.

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

Development validation expectations by tier:

- `docs-only`: no live development smoke required.
- `low`: run development validation when the changed path affects live app rendering or operator commands.
- `medium`: run development validation for Kubernetes manifests, Terraform, Flux wiring, Gateway routes, storage, secrets references, and app behavior changes. Use a smoke-helper lane by default for touched apps when delegation is available.
- `high`: run development validation for the affected app or base path. For shared cluster base changes, include a sequential development base reconcile before app acceptance.

If the development cluster, kubeconfig, required staged development secrets, or required credentials are unavailable, record a documented exception with the blocker and safest substitute checks. A real development validation failure is not an exception; fix the change, rerun validation, or leave the PR incomplete.

Default development validation paths:

- `smoke_profile: whoami`: run `python3 tools/development/verify_branch_deploy.py --app whoami --branch <branch> --slug <slug> --push` when the `whoami` branch profile fits the touched app or acceptance path.
- `--include-cluster-base`: add this flag when the implementation changes resources under `kubernetes/clusters/development`, shared CRDs, controller installs, Gateway base objects, Cilium, cert-manager, NFS CSI, Flux dependency ordering, or app dependencies that must reconcile before branch app validation.
- `smoke_profile: manual`: for apps without automated profiles, run manual development smoke checks that prove the relevant workload, Service, route, storage, secret reference, and app-specific behavior. Record exact commands and observations.
- `smoke_profile: none`: use only for docs-only or local-only changes, unavailable development infrastructure or credentials, missing development branch coverage that cannot be safely emulated manually, or production-only integrations that development cannot represent. Include substitute checks and a follow-up when coverage should be added.

## Helper Lanes

Use helper lanes without breaking the single-owner model:

- `test-helper`: researches risk, proposes or runs failing tests, and reports command output or patch recommendations. The implementation owner remains the only role that applies tracked-file edits.
- `smoke-helper`: prepares or runs development cluster validation, captures exact branch and `HEAD` evidence, and recommends cleanup. The implementation owner remains responsible for final branch state and PR notes.

Helper output belongs in `.codex/tmp/pr-summary.md` or an equivalent local note when it affects verifier review. Include commands, outcomes, skipped checks, and exceptions. Do not create verifier approval files from helper lanes.

## Evidence Audit

Before requesting verifier review, the implementation owner must audit:

- The plan declares the intended TDD and development validation expectations for the risk tier.
- Any skipped failing test, missing smoke profile, unavailable development cluster, unavailable credentials, or other exception is recorded with a reason and substitute checks.
- Test evidence includes the exact commands run and pass/fail result.
- Development validation evidence includes app name, branch, branch slug, exact `HEAD`, smoke profile or documented exception, report path if one was produced, cleanup status, and whether stale reports were ignored or removed.
- Parent/process evidence is internally consistent: active marker, plan, owner attestation, delegation token, branch, clone path, and PR summary all point at the same implementation.

Verifier review must audit the same evidence. If required development validation is stale, missing, or inconsistent with the risk tier, the verifier must request a rerun, run a spot check, or confirm a documented exception before sign-off.
