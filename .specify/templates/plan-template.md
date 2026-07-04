# Implementation Plan: [IMPLEMENTATION]

**Branch**: `codex/[IMPLEMENTATION]` | **Date**: [DATE] | **Spec**:
`specs/[IMPLEMENTATION]/spec.md`

**Input**: Feature specification from `specs/[IMPLEMENTATION]/spec.md`

## Summary

[Summarize the requirement and chosen technical approach.]

## Technical Context

**Risk Tier**: [tiny|low|medium|high]
**Workflow Tier**: [docs-only|low|medium|high if needed by workflow tooling]
**Primary Areas**: [docs, Kubernetes, Terraform, Flux, app, tooling, secrets, etc.]
**Dependencies**: [Spec Kit, Flux, kubectl, terraform, uv, npm, etc. or N/A]
**Storage**: [NFS class expectation or N/A]
**Ingress**: [Gateway API route expectation or N/A]
**Secrets**: [SOPS expectation or N/A]
**Smoke Strategy**: [development profile, synthetic smoke Job, scriptable
Gateway/DNS/browser smoke, or none with reason]
**Fanout Targets**: [independent tasks safe for helper lanes or N/A]
**Development Validation**: [whoami profile, manual smoke, include-cluster-base,
none with reason]
**Post-Implementation SDD Conformance**: [local docs only, upstream Spec Kit
review required, or N/A]

## Constitution Check

*GATE: Must pass before tracked edits and be re-checked before commit.*

- [ ] GitOps source of truth preserved; no durable live-cluster-only state.
- [ ] No production-first mutation; development validation plan or exception is
      recorded for covered changes.
- [ ] Gateway API invariant preserved; no new Kubernetes `Ingress` resources.
- [ ] SOPS invariant preserved; no plaintext secret manifests staged.
- [ ] NFS default considered for PVC-backed workloads.
- [ ] Talos boundary preserved; no SSH-based node operations introduced.
- [ ] Branch is `codex/[IMPLEMENTATION]`; worktree/current-checkout mode is
      intentional and recorded when relevant.
- [ ] Documentation impact identified; docs updated or no-docs rationale
      recorded.
- [ ] PR review/status checks are the review gate.

## Project Structure

### SDD Artifacts

```text
specs/[IMPLEMENTATION]/
├── spec.md
├── plan.md
├── tasks.md
└── evidence.md
```

### Source Or Documentation Changes

```text
[List exact paths expected to change.]
```

## Tiered TDD And Validation Plan

**TDD expectation**: [What failing test or documented exception applies for this
tier.]

**Local checks**:

- `[command]`

**Development smoke**: [Profile, manual commands, include-cluster-base, or none
with reason.]

**Automated smoke preference**: For user-facing, routed, deployed, or
operational changes, prefer automated smoke in this order: development branch
profile; production synthetic smoke or one-off in-cluster Job; scriptable
Gateway/DNS/browser smoke against the exact user URL; manual browser checks only
as supplemental evidence.

**Completion evidence**: For deploy follow-up, record source fetched SHA, target
kustomization or HelmRelease applied SHA, live resource spec, Gateway/listener
match when applicable, and exact user-facing URL result.

**Fanout plan**: [List independent non-conflicting tasks and how results will be
consolidated into evidence.md.]

**Evidence destination**: `specs/[IMPLEMENTATION]/evidence.md`.

## Documentation Impact

[List docs/runbooks/ADRs/generated docs/agent guidance changed, or explain why
none are required.]

## Implementation Steps

1. [Step]
2. [Step]
3. [Step]

## Risks

| Risk | Mitigation |
| ---- | ---------- |
| [Risk] | [Mitigation] |

## Complexity Tracking

> Fill only when the constitution check has a violation that must be justified.

| Violation | Why Needed | Simpler Alternative Rejected Because |
| --------- | ---------- | ------------------------------------ |
| [N/A] | [N/A] | [N/A] |
