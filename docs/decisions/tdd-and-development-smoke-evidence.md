---
id: ADR-0013
status: accepted
scope:
  - codex-harness
  - implementation-workflow
  - development-cluster
  - agent-operations
authority: binding
created: 2026-05-16
last_verified: 2026-05-16
supersedes: []
superseded_by:
---

# TDD And Development Smoke Evidence

## Decision

Implementation plans, PR summaries, and verifier review must use risk-tiered TDD and development validation evidence for repository changes.

Development-cluster validation is required before production-oriented PR completion for covered cluster-affecting changes: Kubernetes manifests, Terraform, Flux wiring, Gateway routes, storage, secrets references, branch overlays, and app behavior. TDD evidence remains risk-tiered and documented. The harness must not add hard gates for TDD or smoke testing until the practice proves stable across routine work; owners and verifiers enforce the requirement through plan, PR, and review evidence.

If the development cluster, kubeconfig, required staged development secrets, or required credentials are unavailable, owners may record a documented exception with substitute checks. Actual development validation failures are not exceptions; the change should be fixed and rerun before production-oriented completion.

The existing single-owner implementation model remains binding. Test-helper and smoke-helper lanes may research, run commands, prepare recommendations, and report evidence, but the implementation owner remains responsible for tracked edits, commits, local workflow files, `.codex/tmp/pr-summary.md`, and final branch state.

## Rationale

- TDD expectations should scale with operational risk instead of forcing the same process onto docs-only changes and cluster-wide changes.
- Development smoke tests are valuable only when their evidence identifies the app, branch, exact `HEAD`, profile, result, and cleanup state.
- The current branch deployment verifier is intentionally narrow, with automated support for `whoami` only while a config-driven app profile model is developed.
- Hard harness gates would be brittle before the team has enough examples of useful tests, smoke profiles, and valid exceptions.
- Preserving the single-owner model keeps responsibility clear even when helper lanes contribute evidence.

## Consequences

- Implementation plans must describe TDD, development validation expectations, and known exceptions in the tests, verification, and risks sections.
- PR summaries must include commands run, development smoke reports or exceptions, documentation impact, and whether generated architecture changed.
- Verifiers must audit declared tests and development validation evidence against the risk tier, spot-check stale or incomplete evidence, and confirm documented exceptions when live validation is unavailable.
- New app work must add or select a smoke profile when practical, or document why development smoke coverage is deferred.
- Hard harness gates, automated profile enforcement, and non-`whoami` deployment verifier behavior are deferred to future implementations.

## Operational Notes

- Use `docs/runbooks/implementation-workflow.md` for risk tiers and helper lane expectations.
- Use `docs/runbooks/development-cluster.md` for smoke report shape, touched-app smoke coverage, and `--include-cluster-base` guidance.
- Use `docs/runbooks/add-app.md` when adding development coverage for a new app.
