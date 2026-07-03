---
status: current
scope:
  - codex-harness
  - implementation-workflow
authority: binding
created: 2026-05-10
last_verified: 2026-07-03
---

# Implementation Workflow

Use this runbook for every repository code change. The binding decision is
`docs/decisions/codex-implementation-workflow.md`.

## Procedure

1. Choose a single implementation name. One implementation maps to branch
   `codex/<implementation>`, directory `specs/<implementation>/`, and one PR.
2. Default to a dedicated worktree for tracked repository changes:

   ```bash
   git fetch origin
   git worktree add /workspaces/homelab-worktrees/<implementation> \
     -b codex/<implementation> origin/main
   ```

   Use the current checkout only when explicitly requested. Sibling clones are
   allowed as a fallback when a worktree is impractical.
3. If ignored local secrets or configs are required, stage them under
   `.codex/tmp/implementation-secrets/<implementation>/` in the main checkout,
   preserving repo-relative paths and never logging contents. Install staged
   files into the worktree or clone before commands that need them.
4. Run the Spec Kit cycle in the implementation worktree or checkout:
   `specify -> plan -> tasks -> implement`.
5. Keep durable implementation context in `specs/<implementation>/`:
   `spec.md`, `plan.md`, `tasks.md`, and `evidence.md`.
6. Make tracked-file changes only on `codex/<implementation>`, never on `main`.
7. Run relevant checks, collect TDD evidence, and collect required development
   validation evidence for covered cluster-affecting changes.
8. Record command outcomes, development validation evidence or exceptions,
   final branch state, and documentation impact in
   `specs/<implementation>/evidence.md`.
9. Commit with a conventional commit message.
10. Create the pull request against `main`. Review gating happens through
    normal GitHub PR review and status checks.

## Guard Gates

The local workflow guard enforces the branch and artifact contract:

- tracked edits on `main` are rejected;
- tracked edits outside `codex/<implementation>` branches are rejected;
- initial bootstrap of `specs/<implementation>/{spec,plan,tasks,evidence}.md`
  is allowed on a new implementation branch;
- after bootstrap, non-bootstrap tracked edits require non-empty `spec.md`,
  `plan.md`, and `tasks.md`;
- push and automatic PR creation require non-empty `evidence.md` as well.

Local owner attestations, verifier attestations, delegation token files, and
exact-`HEAD` verifier approval files are no longer part of the workflow.

## Prompt Catch

When a prompt appears to request tracked repository changes, the prompt-intent
hook reminds agents that the default execution mode is a worktree:

```bash
git fetch origin
git worktree add /workspaces/homelab-worktrees/<implementation> \
  -b codex/<implementation> origin/main
```

If `/workspaces/homelab-worktrees` is unavailable in a local environment, use a
writable sibling location and record the exception in `evidence.md`.

## Risk-Tiered TDD And Development Validation

TDD evidence remains risk-tiered and documented. Development-cluster validation
is required for covered cluster-affecting changes before production-oriented PR
completion, but it is enforced by implementation evidence and PR review rather
than local attestation files. See
`docs/decisions/tdd-and-development-smoke-evidence.md`.

Declare a risk tier in `plan.md`:

- `docs-only`: documentation, generated docs, decisions, runbooks, or agent
  guidance only.
- `low`: narrow code or manifest changes with local-only behavior and low
  operational blast radius.
- `medium`: app behavior, Kubernetes manifests, Flux wiring, Terraform module
  logic, storage, secrets references, or Gateway routes.
- `high`: cluster-scoped controllers, CRDs, networking, storage classes,
  authentication, production traffic paths, secret handling, or changes that can
  affect multiple apps.

Development validation expectations by tier:

- `docs-only`: no live development smoke required.
- `low`: run development validation when the changed path affects live app
  rendering or operator commands.
- `medium`: run development validation for Kubernetes manifests, Terraform,
  Flux wiring, Gateway routes, storage, secrets references, and app behavior
  changes.
- `high`: run development validation for the affected app or base path. For
  shared cluster base changes, include a sequential development base reconcile
  before app acceptance.

If the development cluster, kubeconfig, required staged development secrets, or
required credentials are unavailable, record a documented exception with the
blocker and safest substitute checks. A real development validation failure is
not an exception; fix the change, rerun validation, or leave the PR incomplete.

Default development validation paths:

- `smoke_profile: whoami`: run
  `python3 tools/development/verify_branch_deploy.py --app whoami --branch <branch> --slug <slug> --push`
  when the `whoami` branch profile fits the touched app or acceptance path.
- `--include-cluster-base`: add this flag when shared development base resources
  must reconcile before branch app validation.
- `smoke_profile: manual`: for apps without automated profiles, run manual
  development smoke checks that prove the relevant workload, Service, route,
  storage, secret reference, and app-specific behavior.
- `smoke_profile: none`: use only for docs-only or local-only changes,
  unavailable development infrastructure or credentials, missing development
  branch coverage that cannot be safely emulated manually, or production-only
  integrations that development cannot represent.

## Evidence Audit

Before requesting PR review, audit:

- The plan declares the intended TDD and development validation expectations for
  the risk tier.
- Skipped tests, missing smoke profiles, unavailable infrastructure, or other
  exceptions are recorded with substitute checks.
- Test evidence includes exact commands and pass/fail result.
- Development validation evidence includes app name, branch, branch slug, exact
  `HEAD`, smoke profile or documented exception, report path if one was
  produced, and cleanup status.
