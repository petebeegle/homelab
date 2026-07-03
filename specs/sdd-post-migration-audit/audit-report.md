# SDD Post-Migration Audit Report

**Implementation**: `sdd-post-migration-audit`
**Branch**: `codex/sdd-post-migration-audit`
**Audit timestamp**: 2026-07-03T21:16:30Z
**Owner**: implementation-agent-sdd-post-migration-audit

## Canonical Guidance Boundary

Canonical implementation guidance is limited to:

- `AGENTS.md`
- `docs/runbooks/spec-driven-development.md`
- `docs/runbooks/implementation-workflow.md`
- `docs/decisions/*`
- harness validators under `tools/codex-harness/`

SDD artifacts under `specs/<implementation>/` are durable implementation
records and trace to the canonical sources. They do not replace ADRs, binding
runbooks, AGENTS.md, or validators.

## Spec Kit Routing Verification

- `.specify/memory/constitution.md` routes implementation evidence to
  `specs/<implementation>/` and states that `.codex/tmp/` is local runtime
  scratch.
- `docs/runbooks/spec-driven-development.md` records the Spec Kit initialization
  and fallback commands, artifact ownership, guard behavior, tier mapping, and
  development validation expectations.
- `.codex/retrieval.yaml` now indexes `AGENTS.md`, generated architecture,
  binding decisions, and runbooks. It no longer indexes
  `.codex/memory/approved/**/*.md`.
- `.codex/agents/*.toml` now provides short role pointers and defers workflow
  detail to canonical docs and validators.

## Open PR Classification

Source command:

```sh
gh pr list --state open --json number,title,headRefName,baseRefName,isDraft,mergeStateStatus,statusCheckRollup,updatedAt,url
```

| PR | Branch | Classification | Evidence |
| -- | ------ | -------------- | -------- |
| #315 | `codex/jellyfin-authentik-sso` | Draft, old Codex implementation branch | Draft PR updated 2026-06-16, merge state `DIRTY`, and no check rollup returned. Needs owner decision before reuse or closure. |
| #308 | `renovate/authentik-2026.x` | Fresh Renovate dependency PR | Updated 2026-07-03, merge state `CLEAN`, and CI check runs successful. Treat as active Renovate review, not SDD cleanup backlog. |
| #295 | `codex/jellyfin-oauth-provider-secret-source` | Old Codex implementation branch | Updated 2026-05-24 with historical CI success. Needs rebase/revalidation or closure decision. |
| #287 | `codex/homepage-dashboard` | Old Codex implementation branch | Updated 2026-05-24, merge state `DIRTY`, with historical CI success. Needs rebase/revalidation or closure decision. |
| #263 | `codex/pypi-parser-adoption` | Old Codex tooling branch | Updated 2026-05-17, merge state `DIRTY`, with historical CI success. Needs rebase/revalidation or closure decision. |
| #237 | `codex/unifi-dns-records` | Old Codex Terraform branch | Updated 2026-05-16 with historical CI success. Needs rebase/revalidation, development validation review, or closure decision. |
| #163 | `renovate/ghcr.io-devcontainers-features-terraform-1.x` | Old Renovate dependency PR | Updated 2026-06-30 with historical CI success. Needs dependency freshness review or closure. |

## Centralized Backlog

- `codex/dev-secret-staging-for-smoke`: follow-up PR to stage development secret
  material for smoke validation. This first slice records it only and does not
  implement it.
- Decide whether to rebase, revalidate, merge, or close old Codex PRs #315,
  #295, #287, #263, and #237.
- Review old Renovate PR #163 for dependency freshness versus supersession.
- Keep active review of Renovate PR #308 separate from this docs cleanup.
- Consider a future targeted audit for Codex harness/devcontainer guidance if
  tool code or tests still mention obsolete authority after this docs-only slice.
- After this implementation records residue categories, a non-implementation
  cleanup actor may purge ignored `.codex/tmp` residue in the planner checkout.

## Ignored Residue Categories Recorded Before Cleanup

The planner checkout was inspected without deleting ignored files. Categories
observed under `/workspaces/homelab/.codex/tmp`:

- stale implementation secret staging directories under
  `.codex/tmp/implementation-secrets/`
- inspection clone under `.codex/tmp/inspect/homelab-private`
- observability counters and session files under `.codex/tmp/observability/`
- repository change intent marker `.codex/tmp/repo-change-intent`
- implementation workflow guard state `.codex/tmp/implementation-workflow-guard-state`
- foundry bluegreen rehearse report
  `.codex/tmp/foundry-bluegreen-dev-rehearse.json`
- delegation token directory `.codex/tmp/delegation-tokens/`

No planner-checkout ignored cleanup was performed by this implementation owner.

## Cleanup Performed

- Deleted tracked `.codex/memory/approved/*.md` files because their workflow,
  harness, devcontainer, runbook placement, and commit hygiene content is
  duplicated or superseded by canonical docs and validators.
- Removed `.codex/memory/approved/**/*.md` from `.codex/retrieval.yaml`.
- Rewrote `.codex/agents/*.toml` to short canonical pointers.
- Removed `.codex/runbooks/README.md` because it only documented legacy
  placement. Individual `.codex/runbooks/*.md` files remain for non-canonical
  operator notes.
- Reduced `tools/development/README.md` authority wording to CLI usage guidance
  with a pointer to `docs/runbooks/development-cluster.md`.

## Development Smoke

Development smoke profile: `none`.

Reason: this slice changes documentation, retrieval routing, and agent guidance
only. It does not change Kubernetes, Terraform, Flux, Gateway, storage, secret
references, app behavior, or branch overlays.
