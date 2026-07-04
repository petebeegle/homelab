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
4. Run the Spec Kit cycle in the implementation worktree or checkout as a
   human decision workflow. For meaningful work, use:
   `specify -> clarify -> human spec approval -> plan -> checklist -> human plan approval -> tasks -> analyze -> human implementation approval -> implement -> converge`.
   Tiny wording-only changes and obvious low-risk local edits may skip selected
   quality gates only when the skipped `clarify`, `checklist`, `analyze`, or
   `converge` step and rationale are recorded in evidence.
5. Keep durable implementation context in `specs/<implementation>/`:
   `spec.md`, `plan.md`, `tasks.md`, and `evidence.md`.
6. In `plan.md`, declare the SDD tier, workflow risk tier, smoke strategy,
   fanout targets, and exceptions before implementation edits.
7. In `tasks.md`, mark independent fanout work with `[P]` and keep all
   fanout results coordinated through one `evidence.md`.
8. Make tracked-file changes only on `codex/<implementation>`, never on `main`.
9. Run relevant checks, collect TDD evidence, and collect required development
   validation evidence for covered cluster-affecting changes.
10. Record command outcomes, development validation evidence or exceptions,
   SHAs, user-facing URLs, final branch state, and documentation impact in
   `specs/<implementation>/evidence.md`.
11. Commit with a conventional commit message.
12. Create the pull request against `main`. Review gating happens through
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
Human approval gates are recorded in SDD artifacts and PR review evidence; the
local guard intentionally does not add hard blockers for those gates.

## Human Gate Sequence

Humans provide intent, constraints, and acceptance. Agents draft artifacts and
pause when a decision changes the next phase of work:

- **Spec gate**: After `specify` and any needed `clarify`, confirm the desired
  behavior, non-goals, affected systems, edge cases, and acceptance criteria.
- **Plan gate**: After `plan` and any useful `checklist`, confirm the technical
  approach, blast radius, validation strategy, rollback/exception handling, and
  fit with binding ADRs.
- **Task/analyze gate**: After `tasks` and `analyze`, confirm the work is
  ordered, testable, traceable to requirements, and small enough to implement.
- **Converge/evidence gate**: After implementation, run `converge` or record a
  skipped-converge exception, update artifacts for discoveries, and record final
  evidence before PR handoff.

For `tiny` and clear `low` changes, a single human approval may cover multiple
gates. The evidence must still state which quality gates were skipped and why.

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

Automated smoke is preferred whenever practical. For user-facing, routed,
deployed, or operational changes, choose the strongest available automated
validation in this order:

1. Existing development branch smoke profile.
2. Production synthetic smoke or a one-off in-cluster synthetic Job.
3. Scriptable Gateway, DNS, HTTP, or browser smoke against the exact user URL.
4. Manual browser verification only as supplemental evidence.

Do not report routed or deployed work as complete from pod readiness, Service
probes, render checks, or `Accepted=True` route status alone. Evidence must
identify the layer proved: rendered intent, pushed branch, merged commit,
Flux-fetched source, kustomization-applied revision, live resource spec, and
user-facing behavior. If a layer is not verified, state that explicitly.

## Fanout And Helper Lanes

Use fanout to reduce elapsed time when workstreams are independent and
non-conflicting. Good targets include repo inspection, test design, render
validation, smoke execution, docs/evidence updates, public/private repo audits,
and live read-only verification.

Fanout must be declared in `plan.md`, represented with `[P]` tasks in
`tasks.md`, and consolidated into the implementation's single `evidence.md`.
Do not split responsibility across multiple branches or PRs unless the work is
intentionally decomposed into separate implementations.

Tracked edits that touch the same files should stay sequential unless the
partition is explicit enough to avoid collisions. Read-only validation and
smoke checks are preferred fanout targets.

## Post-Merge Verification

For deploy follow-up, verify the live system in layers before declaring the
change deployed:

1. The GitHub PR is merged and the merge SHA is known.
2. The Flux source has fetched the merge SHA.
3. The target Kustomization or HelmRelease applied the merge SHA.
4. The live resource spec matches the intended rendered state.
5. Gateway listener, DNS, certificate, backend, and route status match the
   intended exposure when applicable.
6. The exact user-facing URL, protocol, path, and network plane return the
   expected HTTP/browser result.

Record each verified layer in `evidence.md` or the PR/deploy handoff. Use
precise status words such as `rendered`, `pushed`, `merged`, `fetched by Flux`,
`applied`, and `verified from user path`.

## Evidence Audit

Before requesting PR review, audit:

- Human gate evidence records spec, plan, task/analysis, and converge status or
  explicit skipped-gate exceptions.
- The plan declares the intended TDD and development validation expectations for
  the risk tier.
- Skipped tests, missing smoke profiles, unavailable infrastructure, or other
  exceptions are recorded with substitute checks.
- Test evidence includes exact commands and pass/fail result.
- Development validation evidence includes app name, branch, branch slug, exact
  `HEAD`, smoke profile or documented exception, report path if one was
  produced, and cleanup status.
- User-facing or deploy evidence includes exact URLs, SHAs, live resource state,
  and automated smoke result when applicable.
- Workflow or template changes include a local SDD audit and, when they change
  Spec Kit behavior or standards, an upstream Spec Kit conformance check.
