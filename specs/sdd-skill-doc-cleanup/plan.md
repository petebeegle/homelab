# Implementation Plan: sdd-skill-doc-cleanup

**Branch**: `codex/sdd-skill-doc-cleanup` | **Date**: 2026-07-03 | **Spec**:
`specs/sdd-skill-doc-cleanup/spec.md`

**Input**: Feature specification from `specs/sdd-skill-doc-cleanup/spec.md`

## Summary

Audit the tracked repo-local agent context after the Spec Kit and guard
migration, then apply the smallest cleanup that leaves generated Spec Kit skills,
custom agent TOML, approved memory, retrieval context, and default documentation
references current and non-overlapping.

## Technical Context

**Risk Tier**: low
**Workflow Tier**: docs-only
**Primary Areas**: agent guidance, custom agent TOML, approved memory, retrieval
context, SDD evidence
**Dependencies**: Spec Kit templates, Codex harness validators, pre-commit,
agnix, Python unittest, uv, npm smoke tests where quick
**Storage**: N/A
**Ingress**: N/A
**Secrets**: No secret changes expected; no plaintext secret manifests staged
**Development Validation**: none; docs-only/local agent configuration cleanup
does not affect live cluster reconciliation or app behavior

## Constitution Check

*GATE: Must pass before tracked edits and be re-checked before commit.*

- [x] GitOps source of truth preserved; no durable live-cluster-only state.
- [x] No production-first mutation; development validation plan or exception is
      recorded for covered changes.
- [x] Gateway API invariant preserved; no new Kubernetes `Ingress` resources.
- [x] SOPS invariant preserved; no plaintext secret manifests staged.
- [x] NFS default considered for PVC-backed workloads.
- [x] Talos boundary preserved; no SSH-based node operations introduced.
- [x] Sibling clone ownership files validated before tracked edits.
- [x] Documentation impact identified; docs updated or no-docs rationale
      recorded.
- [x] Separate verifier approval required before PR creation.

## Project Structure

### SDD Artifacts

```text
specs/sdd-skill-doc-cleanup/
├── spec.md
├── plan.md
├── tasks.md
└── evidence.md
```

### Source Or Documentation Changes

```text
.codex/agents/*.toml
.codex/memory/approved/*.md
.codex/retrieval.yaml
AGENTS.md
PLANS.md
docs/decisions/agent-memory-compaction.md
docs/runbooks/spec-driven-development.md
docs/runbooks/implementation-workflow.md
specs/sdd-skill-doc-cleanup/
```

Only paths that the audit proves stale will be changed.

## Tiered TDD And Validation Plan

**TDD expectation**: No failing code test is required because this is docs-only
and local agent configuration cleanup. Use repository harness and context checks
that cover the edited guidance instead.

**Local checks**:

- `python3 tools/codex-harness/validate_active_implementation.py --marker .codex/tmp/active-implementation --root "$(pwd)" --branch "$(git branch --show-current)"`
- `python3 tools/codex-harness/validate_implementation_plan.py --plan .codex/tmp/implementation-plan.yaml --marker .codex/tmp/active-implementation --root "$(pwd)" --branch "$(git branch --show-current)"`
- `python3 tools/codex-harness/validate_workflow_attestations.py --kind owner --attestation .codex/tmp/implementation-owner-attestation.yaml --marker .codex/tmp/active-implementation --plan .codex/tmp/implementation-plan.yaml --root "$(pwd)" --branch "$(git branch --show-current)"`
- `python3 tools/codex-harness/validate_sdd_context.py --marker .codex/tmp/active-implementation --root "$(pwd)" --branch "$(git branch --show-current)" --require-plan-artifacts`
- `python3 -m unittest discover -s tools/codex-harness/tests`
- `pre-commit run --all-files`
- `python3 tools/architecture/render.py --check`
- `python3 -m unittest discover -s tools/development/tests`
- `python3 -m unittest discover -s tools/context-pack/tests`
- `uv run --project tools/agent-memory pytest tools/agent-memory/tests`
- `npx -y agnix@0.25.0 .`
- Optional if quick: `npm ci && npm test` in `tests/smoke`

**Development smoke**: none; docs-only/local-only cleanup with no Kubernetes,
Terraform, Flux, Gateway, storage, secret, or app behavior changes.

**Evidence destination**: `specs/sdd-skill-doc-cleanup/evidence.md` and
`.codex/tmp/pr-summary.md`.

## Documentation Impact

Agent guidance, retrieval context, approved memory, the memory compaction ADR,
and SDD artifacts may change. Generated architecture is not expected to change.

## Implementation Steps

1. Validate existing workflow marker, implementation plan, owner attestation,
   and delegation token.
2. Bootstrap the required SDD artifacts.
3. Audit tracked scoped files and classify stale references or schema drift.
4. Apply targeted documentation, memory, retrieval, and custom agent config
   cleanup.
5. Run required local checks and record outcomes.
6. Commit with a conventional commit and stop before PR creation.

## Risks

| Risk | Mitigation |
| ---- | ---------- |
| Useful routing guidance could be removed as stale. | Compare against binding runbooks, ADRs, and tracked origin/main files before editing. |
| Generated Spec Kit skills could drift from upstream. | Preserve generated skills and avoid editing them unless required by repo binding policy. |
| Approved memory could duplicate binding workflow policy. | Keep memory advisory and point to canonical ADRs/runbooks rather than restating full policy. |

## Complexity Tracking

> Fill only when the constitution check has a violation that must be justified.

| Violation | Why Needed | Simpler Alternative Rejected Because |
| --------- | ---------- | ------------------------------------ |
| N/A | N/A | N/A |
