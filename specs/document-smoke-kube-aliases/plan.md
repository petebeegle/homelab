# Implementation Plan: document-smoke-kube-aliases

**Branch**: `codex/document-smoke-kube-aliases` | **Date**: 2026-07-04 |
**Spec**: `specs/document-smoke-kube-aliases/spec.md`

**Input**: Feature specification from
`specs/document-smoke-kube-aliases/spec.md`

## Summary

Make a docs-only update to the synthetic smoke runbook so manual smoke commands
use the existing kube aliases when an explicit development or production cluster
context is needed. Keep alias behavior and cluster desired state unchanged.

## Technical Context

**Risk Tier**: tiny
**Workflow Tier**: docs-only
**Primary Areas**: documentation, SDD artifacts
**Dependencies**: local Git, `rg`, Python architecture renderer, SDD context
validator
**Storage**: N/A
**Ingress**: N/A
**Secrets**: No secret manifests or local secret contents are changed
**Development Validation**: none; docs-only change with no Kubernetes desired
state or smoke behavior impact

## Constitution Check

*GATE: Must pass before tracked edits and be re-checked before commit.*

- [x] GitOps source of truth preserved; no durable live-cluster-only state.
- [x] No production-first mutation; development validation exception is
      recorded for this docs-only change.
- [x] Gateway API invariant preserved; no new Kubernetes `Ingress` resources.
- [x] SOPS invariant preserved; no plaintext secret manifests staged.
- [x] NFS default considered for PVC-backed workloads; not applicable.
- [x] Talos boundary preserved; no SSH-based node operations introduced.
- [x] Branch is `codex/document-smoke-kube-aliases`; fallback worktree location
      is recorded because `/workspaces/homelab-worktrees` was not writable.
- [x] Documentation impact identified; synthetic smoke runbook is updated.
- [x] PR review/status checks are the review gate.

## Project Structure

### SDD Artifacts

```text
specs/document-smoke-kube-aliases/
├── spec.md
├── plan.md
├── tasks.md
└── evidence.md
```

### Source Or Documentation Changes

```text
docs/runbooks/synthetic-smoke-tests.md
specs/document-smoke-kube-aliases/
```

## Tiered TDD And Validation Plan

**TDD expectation**: No failing test is required for this docs-only wording
change. The useful validation is focused review, targeted search, generated
architecture check, and SDD context validation.

**Local checks**:

- `rg -n "kube-aliases|kd config current-context|kp create job|synthetic-smoke" docs/runbooks/synthetic-smoke-tests.md`
- `python3 tools/architecture/render.py --check`
- `python3 tools/codex-harness/validate_sdd_context.py --root "$(pwd)" --branch "$(git branch --show-current)" --require-plan-artifacts`

**Development smoke**: none. This docs-only change does not affect Kubernetes
desired state, branch overlays, app behavior, smoke code, Gateway routes,
storage, or secret references.

**Evidence destination**: `specs/document-smoke-kube-aliases/evidence.md`.

## Documentation Impact

Updates `docs/runbooks/synthetic-smoke-tests.md` only. Generated
`docs/architecture.md` is expected to remain unchanged.

## Implementation Steps

1. Create the implementation branch and worktree, using the allowed sibling
   fallback if the default worktree parent is unavailable.
2. Add SDD spec, plan, tasks, and evidence artifacts.
3. Update the synthetic smoke Manual Run section to source the alias script,
   explain development and production aliases, and use `kp` for production
   manual smoke commands.
4. Run focused docs/workflow checks and record outcomes in evidence.
5. Commit with a conventional docs commit.

## Risks

| Risk | Mitigation |
| ---- | ---------- |
| Operators run smoke against the wrong cluster | Include `config current-context` examples and identify each alias target |
| Docs imply alias behavior that drifts from the script | Keep `scripts/kube-aliases.sh` unchanged and name it as the source of truth |
| Live smoke is skipped for a cluster-affecting change | Classify the slice as docs-only and record that no cluster behavior changed |

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
| --------- | ---------- | ------------------------------------ |
| N/A | N/A | N/A |
