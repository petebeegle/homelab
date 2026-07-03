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

Use this runbook to plan Homelab changes with Spec Kit while preserving the
mandatory implementation workflow and binding ADRs.

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

The implementation owner also owns local runtime files under `.codex/tmp/` in
the sibling clone. These files are ignored and are not durable documentation.

Verifier files under `.codex/tmp/` are owned by a separate verifier and are not
created by the implementation owner.

## Enforced Guard Behavior

The harness treats `specs/<implementation>/` as durable implementation context.
After the initial SDD artifact bootstrap, non-bootstrap tracked edits require a
valid implementation marker, implementation plan, owner attestation, delegation
token, and non-empty:

- `specs/<implementation>/spec.md`
- `specs/<implementation>/plan.md`
- `specs/<implementation>/tasks.md`

`specs/<implementation>/evidence.md` is required before verifier approval,
automatic PR creation, final handoff, and non-smoke pushes. If evidence records
an explicit final, verified, approved, branch, or current `HEAD`, the recorded
SHA must match the current branch `HEAD`.

Automatic PR creation runs these gates itself through
`.codex/scripts/create_implementation_pr.sh --auto`; Stop-hook ordering is not
the enforcement boundary.

Development smoke validation may push the active implementation branch to
`origin codex/<implementation>` before verifier approval only from a valid
implementation clone with non-empty `spec.md`, `plan.md`, and `tasks.md`.
Verifier approval for the exact `HEAD` remains mandatory for PR creation, final
handoff, and non-smoke pushes.

## Spec Persistence

Keep useful decisions, assumptions, acceptance criteria, test outcomes, smoke
evidence, and exceptions in `specs/<implementation>/`. Use `.codex/tmp/` only
for active workflow state such as markers, attestations, delegation tokens,
verifier approval, and draft PR summaries.

If future operators need the information after the branch is merged, it belongs
in a committed spec, runbook, ADR, or generated documentation.

## Tiered Workflow

Use the SDD tier in the spec and plan, and map it to the implementation workflow
risk tier when writing `.codex/tmp/implementation-plan.yaml`.

| SDD tier | Use for | Expected evidence |
| -------- | ------- | ----------------- |
| `tiny` | Typos, comments, links, or wording-only changes | Review check and any cheap file-specific validator |
| `low` | Narrow local code, tooling, generated docs, or low-risk guidance changes | Relevant local checks; focused test when executable code has a reasonable test seam |
| `medium` | App behavior, Kubernetes manifests, Flux wiring, Terraform logic, Gateway routes, storage, secret references, or branch overlays | Focused render/unit checks plus development validation or a documented unavailable-infrastructure exception |
| `high` | Cluster-scoped controllers, CRDs, networking, storage classes, authentication, production traffic paths, secret handling, or multi-app impact | Helper-lane review where available, broad local checks, and development validation for affected apps or shared base paths |

`docs-only` from the implementation workflow can be recorded alongside `tiny` or
`low` when harness wording requires that exact tier.

## Procedure

1. Create a named implementation and branch plan in the main checkout.
2. Create or reuse the sibling clone required by
   `docs/runbooks/implementation-workflow.md`.
3. Before tracked edits, create and validate `.codex/tmp/active-implementation`,
   `.codex/tmp/implementation-plan.yaml`,
   `.codex/tmp/implementation-owner-attestation.yaml`, and delegation token
   evidence.
4. Create `specs/<implementation>/spec.md` from
   `.specify/templates/spec-template.md`.
5. Create `specs/<implementation>/plan.md` from
   `.specify/templates/plan-template.md`.
6. Create `specs/<implementation>/tasks.md` from
   `.specify/templates/tasks-template.md`.
7. Create `specs/<implementation>/evidence.md` from
   `.specify/templates/evidence-template.md`.
8. Implement the change in the sibling clone only.
9. Record command outcomes, development validation, exceptions, final `HEAD`,
   and documentation impact in `evidence.md`.
10. Write `.codex/tmp/pr-summary.md` from the plan and evidence before verifier
    handoff.

## Development Validation

Development-cluster validation follows
`docs/decisions/tdd-and-development-smoke-evidence.md` and
`docs/runbooks/development-cluster.md`.

Use `smoke_profile: none` only for docs-only/local-only work or when required
development infrastructure or credentials are unavailable. Record the reason and
substitute checks in both `evidence.md` and `.codex/tmp/pr-summary.md`.

Use `--include-cluster-base` when shared development base resources must
reconcile before app acceptance.

## Review Checklist

- The spec links relevant binding ADRs and runbooks.
- The plan declares SDD tier, workflow tier when needed, tests, smoke
  expectations, docs impact, and risks.
- Tasks are concrete enough for an implementation owner to execute.
- Evidence includes exact command outcomes and exceptions.
- `.codex/tmp` files are consistent with the implementation identity and branch.
- The implementation owner did not create verifier approval.
