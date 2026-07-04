# Implementation Plan: sdd-post-migration-audit

**Branch**: `codex/sdd-post-migration-audit` | **Date**: 2026-07-03 |
**Spec**: `specs/sdd-post-migration-audit/spec.md`

**Input**: Feature specification from
`specs/sdd-post-migration-audit/spec.md`

## Summary

Perform a docs-only post-migration audit and cleanup. The implementation keeps
the binding workflow in canonical docs, removes duplicated approved memory
retrieval, shortens agent prompts to canonical pointers, and records audit
findings plus backlog in durable SDD artifacts.

## Technical Context

**Risk Tier**: tiny
**Workflow Tier**: docs-only
**Primary Areas**: SDD artifacts, Codex-local documentation, retrieval manifest,
agent prompt configuration, development tool README
**Dependencies**: local Git, `rg`, Python policy and architecture checks, GitHub
CLI when available for live PR audit
**Storage**: N/A
**Ingress**: N/A
**Secrets**: No secret manifests or local secret contents are changed
**Development Validation**: none; docs-only/local-only change with no cluster
behavior impact

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
specs/sdd-post-migration-audit/
├── spec.md
├── plan.md
├── tasks.md
├── evidence.md
└── audit-report.md
```

### Source Or Documentation Changes

```text
.codex/agents/*.toml
.codex/memory/approved/*.md
.codex/retrieval.yaml
.codex/runbooks/README.md
tools/development/README.md
specs/sdd-post-migration-audit/
```

## Tiered TDD And Validation Plan

**TDD expectation**: No failing code test is required for this docs-only slice.
The smallest useful validation is targeted repository search plus policy and
generated architecture checks.

**Local checks**:

- `python3 tools/policy/check_retrieval_manifest.py`
- `python3 tools/architecture/render.py --check`
- targeted `rg` checks for stale `.codex/memory/approved` retrieval and
  obsolete canonical guidance
- `pre-commit run --all-files` if practical

**Development smoke**: none. The change is docs-only/local-only and does not
affect manifests, branch overlays, app behavior, or cluster operations.

**Evidence destination**: `specs/sdd-post-migration-audit/evidence.md` and
`.codex/tmp/pr-summary.md`.

## Documentation Impact

This slice changes Codex-local documentation and durable SDD evidence. It does
not update binding ADRs or generated `docs/architecture.md` because no
architecture, Kubernetes, or Terraform source changes are made.

## Implementation Steps

1. Bootstrap workflow metadata and SDD artifacts in the assigned sibling clone.
2. Audit current Spec Kit routing, open PRs, local residue categories, and stale
   guidance references.
3. Delete duplicated approved memory notes and remove their retrieval routing.
4. Shorten `.codex/agents/*.toml` guidance to canonical pointers.
5. Prune `.codex/runbooks/README.md` and `tools/development/README.md` authority
   wording while preserving useful CLI usage.
6. Record audit findings, validation outcomes, development smoke exception, and
   final branch state.
7. Commit with a conventional commit and leave verifier approval uncreated.

## Risks

| Risk | Mitigation |
| ---- | ---------- |
| Useful non-canonical local notes are over-pruned | Inspect each target file and preserve non-canonical operational usage where requested |
| Audit data ages quickly | Record source command and timestamp in the audit report |
| Retrieval cleanup leaves hidden references | Run targeted `rg` checks and the retrieval manifest policy check |
| Pre-commit is unavailable or impractical | Record a clear exception and substitute focused checks |

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
| --------- | ---------- | ------------------------------------ |
| N/A | N/A | N/A |
