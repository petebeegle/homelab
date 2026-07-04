# Implementation Plan: sdd-agent-workflow-standards

**Branch**: `codex/sdd-agent-workflow-standards` | **Date**: 2026-07-04 |
**Spec**: `specs/sdd-agent-workflow-standards/spec.md`

**Input**: Feature specification from
`specs/sdd-agent-workflow-standards/spec.md`

## Summary

Strengthen Homelab's agent workflow standards by updating the SDD and
implementation runbooks plus Spec Kit templates. The change makes automated
smoke preference, fanout coordination, exact evidence, and upstream SDD
conformance explicit for future implementations.

## Technical Context

**Risk Tier**: low
**Workflow Tier**: docs-only
**Primary Areas**: docs, Spec Kit templates, agent guidance
**Dependencies**: Git, Python for repo validators, internet access for upstream
Spec Kit conformance review
**Storage**: N/A
**Ingress**: N/A
**Secrets**: N/A
**Development Validation**: none; docs/template-only change with no live app or
cluster behavior

## Constitution Check

*GATE: Must pass before tracked edits and be re-checked before commit.*

- [x] GitOps source of truth preserved; no durable live-cluster-only state.
- [x] No production-first mutation; development validation exception is
      recorded because this is docs/template-only.
- [x] Gateway API invariant preserved; no new Kubernetes `Ingress` resources.
- [x] SOPS invariant preserved; no plaintext secret manifests staged.
- [x] NFS default considered for PVC-backed workloads; not applicable.
- [x] Talos boundary preserved; no SSH-based node operations introduced.
- [x] Branch is `codex/sdd-agent-workflow-standards`; sibling worktree fallback
      is intentional because `/workspaces/homelab-worktrees` is absent.
- [x] Documentation impact identified; docs and templates will be updated.
- [x] PR review/status checks are the review gate.

## Project Structure

### SDD Artifacts

```text
specs/sdd-agent-workflow-standards/
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
.specify/templates/plan-template.md
.specify/templates/tasks-template.md
.specify/templates/evidence-template.md
specs/sdd-agent-workflow-standards/
```

## Tiered TDD And Validation Plan

**TDD expectation**: No failing-code test seam is appropriate for docs/template
guidance. Validate by SDD context checks, generated architecture check, targeted
content inspection, and upstream Spec Kit conformance review.

**Local checks**:

- `python3 tools/codex-harness/validate_sdd_context.py --root "$(pwd)" --branch "$(git branch --show-current)" --require-plan-artifacts`
- `python3 tools/architecture/render.py --check`
- `git diff --check`
- targeted `rg` checks for smoke, fanout, and upstream conformance language

**Development smoke**: none; this implementation changes documentation and
templates only.

**Evidence destination**:
`specs/sdd-agent-workflow-standards/evidence.md`.

## Documentation Impact

Update workflow runbooks, top-level agent guidance, and Spec Kit templates.
`docs/architecture.md` is not expected to change because no Kubernetes or
Terraform source changes are made.

## Implementation Steps

1. Bootstrap SDD artifacts for this implementation.
2. Update workflow docs and templates with smoke, fanout, exact evidence, and
   upstream conformance expectations.
3. Validate local docs/template state and record upstream Spec Kit conformance.
4. Commit and open a PR.

## Risks

| Risk | Mitigation |
| ---- | ---------- |
| Guidance becomes too broad to follow | Keep rules tied to concrete artifacts and evidence fields. |
| Online SDD guidance drifts | Record upstream URLs and make repo-local docs binding when stricter. |
| Fanout causes file conflicts | Require fanout tasks to be independent and consolidated through one evidence file. |

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
| --------- | ---------- | ------------------------------------ |
| N/A | N/A | N/A |
