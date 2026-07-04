# Implementation Plan: sdd-human-gated-speckit-flow

**Branch**: `codex/sdd-human-gated-speckit-flow` | **Date**: 2026-07-04 |
**Spec**: `specs/sdd-human-gated-speckit-flow/spec.md`

**Input**: Feature specification from
`specs/sdd-human-gated-speckit-flow/spec.md`

## Summary

Repair Homelab's SDD workflow guidance so future meaningful changes are driven
by human-approved intent artifacts before code. The implementation updates
runbooks, templates, and workflow YAML to include clarify, checklist, analyze,
and converge gates, while keeping enforcement lightweight through evidence.

## Technical Context

**Risk Tier**: low
**Workflow Tier**: docs-only
**Primary Areas**: documentation, Spec Kit templates, workflow metadata, agent guidance
**Dependencies**: Git, Python local validators, upstream Spec Kit docs/repo review
**Storage**: N/A
**Ingress**: N/A
**Secrets**: N/A
**Smoke Strategy**: none; docs/template-only change with no live user path
**Fanout Targets**: read-only validation and content inspection only
**Development Validation**: none; no Kubernetes, Terraform, Flux, Gateway, app,
storage, or secret behavior changes
**Post-Implementation SDD Conformance**: upstream Spec Kit review required

## Human Gates

**Spec Gate**: Approved by user in the implementation prompt through the
provided plan/spec intent. This implementation records the gate as satisfied by
the explicit "PLEASE IMPLEMENT THIS PLAN" request.

**Plan Gate**: Approved by user in the implementation prompt. No additional
technical decision remains open.

**Task/Analyze Gate**: This implementation is low-risk docs/template work.
`analyze` is represented by targeted consistency checks and recorded in
evidence instead of a hard blocker.

**Skipped Gate Exceptions**: `clarify` and `checklist` are skipped for this
implementation because the user supplied a decision-complete plan and selected
docs-and-evidence enforcement in the prior planning turn.

## Constitution Check

*GATE: Must pass before tracked edits and be re-checked before commit.*

- [x] GitOps source of truth preserved; no durable live-cluster-only state.
- [x] No production-first mutation; development validation exception is
      recorded because this is docs/template-only.
- [x] Gateway API invariant preserved; no new Kubernetes `Ingress` resources.
- [x] SOPS invariant preserved; no plaintext secret manifests staged.
- [x] NFS default considered for PVC-backed workloads; not applicable.
- [x] Talos boundary preserved; no SSH-based node operations introduced.
- [x] Branch is `codex/sdd-human-gated-speckit-flow`; sibling worktree fallback
      is intentional because `/workspaces/homelab-worktrees` is not writable.
- [x] Documentation impact identified; runbooks, templates, workflow YAML, and
      agent guidance will be updated.
- [x] PR review/status checks are the review gate.

## Project Structure

### SDD Artifacts

```text
specs/sdd-human-gated-speckit-flow/
├── spec.md
├── plan.md
├── tasks.md
└── evidence.md
```

### Source Or Documentation Changes

```text
AGENTS.md
docs/runbooks/spec-driven-development.md
docs/runbooks/implementation-workflow.md
.specify/templates/spec-template.md
.specify/templates/plan-template.md
.specify/templates/tasks-template.md
.specify/templates/evidence-template.md
.specify/workflows/speckit/workflow.yml
specs/sdd-human-gated-speckit-flow/
```

## Tiered TDD And Validation Plan

**TDD expectation**: No failing-code test seam is appropriate for docs/template
guidance. Validate with SDD context checks, generated architecture check,
targeted content inspections, YAML review, and `git diff --check`.

**Local checks**:

- `python3 tools/codex-harness/validate_sdd_context.py --root "$(pwd)" --branch "$(git branch --show-current)" --require-plan-artifacts`
- `python3 tools/architecture/render.py --check`
- `git diff --check`
- targeted `rg` checks for `clarify`, `checklist`, `analyze`, `converge`,
  `human gate`, and absence of `Spec And Plan` in
  `.specify/templates/tasks-template.md`

**Development smoke**: none; docs/template-only change.

**Automated smoke preference**: Not applicable to this change because there is
no user-facing, routed, deployed, or operational runtime path.

**Completion evidence**: Record validation outcomes, skipped gate exceptions,
docs-only smoke exception, final branch, and final `HEAD`.

**Fanout plan**: Validation checks may run independently after edits. Tracked
edits stay sequential because several files describe the same workflow contract.

**Evidence destination**:
`specs/sdd-human-gated-speckit-flow/evidence.md`.

## Documentation Impact

Update workflow runbooks, top-level agent guidance, Spec Kit templates, and the
Spec Kit workflow YAML. `docs/architecture.md` is not expected to change because
no Kubernetes or Terraform source changes are made.

## Implementation Steps

1. Bootstrap SDD artifacts for this implementation.
2. Update runbooks and AGENTS guidance to describe human-gated SDD.
3. Update templates and workflow YAML to include full quality-gate sequence and
   evidence fields.
4. Run local validation and targeted content checks.
5. Record evidence, review diff, commit, and prepare PR handoff.

## Risks

| Risk | Mitigation |
| ---- | ---------- |
| Guidance becomes too ceremonial for tiny fixes | Preserve lightweight path with explicit skipped-gate exceptions. |
| Workflow YAML references commands unavailable in some integrations | Keep commands aligned to upstream Spec Kit names and document repo-local evidence as the binding fallback. |
| Templates become inconsistent with runbooks | Use targeted content checks and manual YAML/order inspection before handoff. |

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
| --------- | ---------- | ------------------------------------ |
| N/A | N/A | N/A |
