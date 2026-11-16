---
id: ADR-0016
status: accepted
scope:
  - implementation-workflow
  - development-cluster
  - agent-operations
  - agent-memory
authority: binding
created: 2026-11-16
last_verified: 2026-11-16
supersedes:
  - ADR-0007
  - ADR-0012
  - ADR-0013
superseded_by:
---

# PR-Gated Change Workflow

## Decision

Repository changes are proven by pull-request checks, not by per-change
process artifacts.

1. **One branch, one PR.** Never commit to `main` directly. Work in a branch,
   preferably a dedicated worktree so concurrent sessions stay isolated, and
   merge through a PR whose required checks pass.
2. **No per-PR Spec Kit artifacts.** `specs/<implementation>/` (`spec.md`,
   `plan.md`, `tasks.md`, `evidence.md`) is no longer required for any change,
   and no hook or push guard may require it. For work large enough to need a
   written design or plan, put it under `docs/superpowers/specs/` and
   `docs/superpowers/plans/`; that is a judgment call, not a gate.
3. **The development smoke check is the evidence for the apps it covers.**
   `dev-smoke` deploys a PR's change to the development cluster and tests it
   before merge. It may be made a required check on `main` once it has run
   stably; that is tracked in GitHub issue #477. This removes ADR-0013's
   deferral of hard smoke gates.
4. **Everything `dev-smoke` does not cover still needs development validation.**
   For cluster-affecting changes it reports as "not smoke-tested" (Terraform,
   Flux wiring, infrastructure, Gateway routes, storage, secret references, and
   apps without a smoke profile), validate in the development cluster before
   merging and say in the PR description what was run and what it showed. If the
   development cluster or its credentials are unavailable, say so and list the
   substitute checks. A real validation failure is not an exception: fix it and
   rerun.
5. **Automatic merging is limited.** Only Renovate, only non-major updates,
   only apps with a smoke profile, and only after `dev-smoke` is a required
   check.
6. **Tests come first, by review.** Write a failing test before the code where
   the change has testable behaviour. This is enforced by PR review, not by a
   harness gate.
7. **Two local safety guards stay:** the SOPS guard (no unencrypted Secret
   manifests) and the Terraform plan guard (no `terraform apply` without a
   plan). Other agent hooks are optional conveniences and may be removed.
8. **Repo-local agent memory compaction is retired.** `tools/agent-memory` and
   `.codex/memory/` were never populated; agents use their own memory
   facilities.

## Rationale

- The Spec Kit layer (hooks, skills, templates, validators) grew to about
  9,000 lines and 325 files under `specs/`, close to the size of the whole
  `kubernetes/` tree, while the evidence it collected was hand-written.
- A check that deploys the change and tests it is stronger evidence than an
  `evidence.md` that says someone did.
- ADR-0013 deferred hard smoke gates "until the practice proves stable". The
  gate now exists, was proven on real PRs (including PRs that must fail), and
  becomes required only after a stability period.
- `dev-smoke` covers two apps today, so rule 4 keeps ADR-0013's development
  validation requirement for everything else in a lighter form.
- Process documented in `docs/superpowers/specs/2026-11-15-process-layer-audit.md`.

## Consequences

- AGENTS.md, the Spec Kit runbooks, the Spec Kit skills, `.specify/`, the
  implementation-workflow and push guards, and the SDD validators are removed
  or rewritten to match this record.
- Existing `specs/` directories are history. Nothing may depend on them.
- PR descriptions carry the validation statement that rule 4 requires.
- Expanding smoke coverage (more app profiles, branch overlays built from the
  real manifests) is the way to shrink rule 4's manual share.
