# Implementation Plan: sdd-workflow-guards

**Branch**: `codex/sdd-workflow-guards` | **Date**: 2026-07-03 | **Spec**:
`specs/sdd-workflow-guards/spec.md`

**Input**: Feature specification from
`specs/sdd-workflow-guards/spec.md`

## Summary

Add reusable SDD artifact validation to the Codex harness, wire it into tracked
edit guards, verifier approval/PR creation gates, and push guard tests, and
document the resulting workflow contract. The implementation keeps runtime
markers in `.codex/tmp/` while making `specs/<implementation>/` the durable
context required for normal implementation progress.

## Technical Context

**Risk Tier**: low
**Workflow Tier**: low
**Primary Areas**: Codex harness, hooks, PR script, tests, runbooks
**Dependencies**: Python standard library, shell, git, GitHub CLI for real PR
creation paths
**Storage**: N/A
**Ingress**: N/A
**Secrets**: No new secrets; `.codex/tmp` token evidence stays ignored
**Development Validation**: none; local-only workflow guard changes with no
cluster-facing manifests or app behavior

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
specs/sdd-workflow-guards/
├── spec.md
├── plan.md
├── tasks.md
└── evidence.md
```

### Source Or Documentation Changes

```text
.codex/hooks/implementation_workflow_guard.sh
.codex/hooks/verifier_push_guard.sh
.codex/scripts/create_implementation_pr.sh
tools/codex-harness/
tools/codex-harness/tests/
docs/runbooks/spec-driven-development.md
docs/runbooks/implementation-workflow.md
specs/sdd-workflow-guards/
```

## Tiered TDD And Validation Plan

**TDD expectation**: Add focused unit tests for the changed harness and script
behavior. Because this is a guard-hardening change rather than a bug with an
existing failing fixture, tests may be added with implementation and must cover
the requested pass/fail cases.

**Local checks**:

- `python3 -m unittest discover -s tools/codex-harness/tests`
- `pre-commit run --all-files`
- `python3 tools/architecture/render.py --check`
- `python3 -m unittest discover -s tools/development/tests`
- `python3 -m unittest discover -s tools/context-pack/tests`
- `uv run --project tools/agent-memory pytest tools/agent-memory/tests`
- `npx -y agnix@0.25.0 .`

**Development smoke**: none; changes are local harness, hooks, and docs only.

**Evidence destination**: `specs/sdd-workflow-guards/evidence.md` and
`.codex/tmp/pr-summary.md`.

## Documentation Impact

Update `docs/runbooks/spec-driven-development.md` and
`docs/runbooks/implementation-workflow.md` only where needed to describe the new
guard gates, evidence freshness check, and smoke push exception.

## Implementation Steps

1. Inspect existing hook, push guard, PR script, validators, and tests.
2. Add reusable SDD context validation helper or script entrypoint with focused
   tests.
3. Wire required checks into tracked edit guard behavior, verifier/PR gates, and
   push guard behavior.
4. Update docs for the enforced behavior.
5. Run feasible checks and record all command evidence.
6. Commit with a conventional commit and report final `HEAD` without creating
   verifier approval or a PR.

## Risks

| Risk | Mitigation |
| ---- | ---------- |
| SDD artifact gate blocks bootstrap edits needed to create artifacts | Allow bootstrap/spec artifact creation while requiring artifacts for later non-bootstrap tracked edits. |
| Smoke push exception weakens verifier gates | Scope the exception to active `codex/<implementation>` branch pushes from a valid implementation clone/spec context only. |
| PR creation tests accidentally invoke network or `gh` | Keep tests in dry-run or stubbed command paths. |

## Complexity Tracking

> Fill only when the constitution check has a violation that must be justified.

| Violation | Why Needed | Simpler Alternative Rejected Because |
| --------- | ---------- | ------------------------------------ |
| N/A | N/A | N/A |
