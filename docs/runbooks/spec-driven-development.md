---
status: current
scope:
  - spec-driven-development
  - implementation-workflow
  - agent-operations
authority: operational
created: 2026-07-03
last_verified: 2026-07-03
---

# Spec-Driven Development

Use this runbook to plan Homelab changes with Spec Kit while preserving binding
ADRs and local branch/artifact guards.

## Authority

Spec Kit artifacts are durable planning and evidence records. They do not
replace:

- `AGENTS.md`
- `docs/runbooks/implementation-workflow.md`
- binding ADRs under `docs/decisions/`
- harness validators under `tools/codex-harness/`

When an SDD artifact conflicts with a binding ADR, runbook, or validator, follow
the binding source and update the SDD artifact.

## Spec Kit Version And Upgrade Check

Before changing Spec Kit scaffolding, record the installed version and supported
integration:

```bash
uvx --from git+https://github.com/github/spec-kit.git specify init --help
```

For first-time initialization in this repo, prefer:

```bash
uvx --from git+https://github.com/github/spec-kit.git specify init --here --force --integration codex
```

If the `codex` integration is unavailable, use:

```bash
uvx --from git+https://github.com/github/spec-kit.git specify init --here --force --integration generic
```

Record the fallback in:

- `specs/<implementation>/evidence.md`
- `.codex/tmp/pr-summary.md`
- any runbook or spec updated by the implementation

The initialized version is also recorded in `.specify/init-options.json`.
Review `.specify/integration.json` when checking whether integration settings
changed.

## Artifact Ownership

Each implementation owns:

- `specs/<implementation>/spec.md`
- `specs/<implementation>/plan.md`
- `specs/<implementation>/tasks.md`
- `specs/<implementation>/evidence.md`

Runtime files under `.codex/tmp/` are ignored and are not durable
documentation. Durable implementation context belongs in `specs/<implementation>/`.

## Upstream Conformance

Homelab follows the upstream Spec Kit phase order: Spec -> Plan -> Tasks ->
Implement. Upstream Spec Kit documentation is useful for process checks and
tooling updates, but repo-local sources remain binding when they are stricter:
`AGENTS.md`, this runbook, `docs/runbooks/implementation-workflow.md`, binding
ADRs, and harness validators.

After implementation, evidence should include a short SDD conformance check
against both local workflow sources and upstream Spec Kit guidance when the
change alters agent workflow, Spec Kit templates, or implementation standards.
The check should confirm that the spec defines behavior before implementation,
the plan records technical approach and constraints, tasks are actionable, and
implementation evidence is reconciled back into the artifact set.

## Enforced Guard Behavior

The harness treats `specs/<implementation>/` as durable implementation context.
After the initial SDD artifact bootstrap, non-bootstrap tracked edits require
branch `codex/<implementation>` and non-empty:

- `specs/<implementation>/spec.md`
- `specs/<implementation>/plan.md`
- `specs/<implementation>/tasks.md`

`specs/<implementation>/evidence.md` is required before push and automatic PR
creation. If evidence records an explicit final, verified, approved, branch, or
current `HEAD`, the recorded SHA must match the current branch `HEAD`.

Automatic PR creation runs these gates itself through
`.codex/scripts/create_implementation_pr.sh --auto`; Stop-hook ordering is not
the enforcement boundary.

## Spec Persistence

Keep useful decisions, assumptions, acceptance criteria, test outcomes, smoke
evidence, and exceptions in `specs/<implementation>/`. Use `.codex/tmp/` only
for local scratch state such as prompt-intent markers and draft PR summaries.

If future operators need the information after the branch is merged, it belongs
in a committed spec, runbook, ADR, or generated documentation.

When requirements change during implementation or acceptance, update the
nearest SDD artifact before continuing. Adjust `spec.md` for intended behavior,
`plan.md` for approach or validation strategy, `tasks.md` for execution order or
fanout, and `evidence.md` for observed results and exceptions.

## Tiered Workflow

Use the SDD tier in the spec and plan, and map it to the implementation workflow
risk tier in `plan.md` when needed.

| SDD tier | Use for | Expected evidence |
| -------- | ------- | ----------------- |
| `tiny` | Typos, comments, links, or wording-only changes | Review check and any cheap file-specific validator |
| `low` | Narrow local code, tooling, generated docs, or low-risk guidance changes | Relevant local checks; focused test when executable code has a reasonable test seam |
| `medium` | App behavior, Kubernetes manifests, Flux wiring, Terraform logic, Gateway routes, storage, secret references, or branch overlays | Focused render/unit checks plus development validation or a documented unavailable-infrastructure exception |
| `high` | Cluster-scoped controllers, CRDs, networking, storage classes, authentication, production traffic paths, secret handling, or multi-app impact | Helper-lane review where available, broad local checks, and development validation for affected apps or shared base paths |

`docs-only` from the implementation workflow can be recorded alongside `tiny` or
`low` when harness wording requires that exact tier.

## Procedure

1. Create a named implementation.
2. Create or reuse the default worktree:
   `/workspaces/homelab-worktrees/<implementation>` on branch
   `codex/<implementation>`.
3. Create `specs/<implementation>/spec.md` from
   `.specify/templates/spec-template.md`.
4. Create `specs/<implementation>/plan.md` from
   `.specify/templates/plan-template.md`.
5. Create `specs/<implementation>/tasks.md` from
   `.specify/templates/tasks-template.md`.
6. Create `specs/<implementation>/evidence.md` from
   `.specify/templates/evidence-template.md`.
7. Implement the change in the worktree or explicitly selected checkout.
8. Record command outcomes, development validation, exceptions, final `HEAD`,
   and documentation impact in `evidence.md`.

## Development Validation

Development-cluster validation follows
`docs/decisions/tdd-and-development-smoke-evidence.md` and
`docs/runbooks/development-cluster.md`.

Prefer automated smoke evidence for every user-facing, routed, deployed, or
operational change. Use the strongest practical automated signal in this order:

1. Existing development branch smoke profile.
2. Production synthetic smoke or a one-off in-cluster synthetic Job.
3. Scriptable Gateway, DNS, HTTP, or browser smoke against the exact user URL.
4. Manual browser verification only as supplemental evidence.

Use `smoke_profile: none` only for docs-only/local-only work or when required
development infrastructure or credentials are unavailable. Record the reason and
substitute checks in `evidence.md`. A routed or deployed change is not complete
from pod readiness, Service probes, render checks, or `Accepted=True` route
status alone; evidence must prove the intended user path or clearly state which
layer remains unverified.

Use `--include-cluster-base` when shared development base resources must
reconcile before app acceptance.

## Fanout

Use fanout when tasks are independent and non-conflicting. Good fanout targets
include repo inspection, test design, render validation, smoke execution,
documentation/evidence updates, public/private repo audits, and live read-only
verification. Mark parallelizable work with `[P]` in `tasks.md`, keep tracked
edits coordinated through the single implementation branch, and consolidate all
results into one `evidence.md`.

Do not fan out tracked edits that touch the same files unless the task
boundaries are explicit enough to avoid collisions. Fanout does not replace the
one implementation, one branch, one `specs/<implementation>/`, one PR contract.

## Review Checklist

- The spec links relevant binding ADRs and runbooks.
- The plan declares SDD tier, workflow tier when needed, tests, smoke
  expectations, fanout targets, docs impact, and risks.
- Tasks are concrete enough for an implementation owner to execute.
- Evidence includes exact command outcomes, SHAs, URLs when applicable, smoke
  results, skipped checks, final live verification, and exceptions.
- The branch is `codex/<implementation>` and artifacts live under matching
  `specs/<implementation>/`.
