# Implementation Plan: sdd-speckit-foundation

**Branch**: `codex/sdd-speckit-foundation` | **Date**: 2026-07-03 |
**Spec**: `specs/sdd-speckit-foundation/spec.md`

## Summary

Initialize Spec Kit with Codex integration, customize its constitution and
templates for Homelab's mandatory workflow, add a new SDD runbook, shorten
`AGENTS.md` into a router, and commit the first durable SDD artifacts.

## Technical Context

**Risk Tier**: low
**Workflow Tier**: docs-only
**Primary Areas**: agent guidance, Spec Kit scaffolding, documentation, SDD
artifacts
**Dependencies**: `uvx`, upstream `github/spec-kit`, Python test tooling,
pre-commit, `uv`, npm for smoke tests
**Storage**: N/A
**Ingress**: N/A
**Secrets**: No secret manifests changed; SOPS invariant documented
**Development Validation**: none; no Kubernetes, Terraform, Flux, Gateway,
storage, secret reference, branch overlay, or app behavior changes

## Constitution Check

- [x] GitOps source of truth preserved; no durable live-cluster-only state.
- [x] No production-first mutation; development validation exception is recorded
      because this is docs-only scaffolding.
- [x] Gateway API invariant preserved; no new Kubernetes `Ingress` resources.
- [x] SOPS invariant preserved; no plaintext secret manifests staged.
- [x] NFS default considered; no PVC-backed workload changes.
- [x] Talos boundary preserved; no SSH-based node operations introduced.
- [x] Sibling clone ownership files validated before tracked edits.
- [x] Documentation impact identified; docs and agent guidance are the output.
- [x] Separate verifier approval required before PR creation.

## Project Structure

### SDD Artifacts

```text
specs/sdd-speckit-foundation/
├── spec.md
├── plan.md
├── tasks.md
└── evidence.md
```

### Source Or Documentation Changes

```text
AGENTS.md
.agents/skills/
.specify/
docs/runbooks/spec-driven-development.md
specs/sdd-speckit-foundation/
```

## Tiered TDD And Validation Plan

**TDD expectation**: No red test is required for docs-only scaffolding. The
substitute is a combination of workflow validators, documentation review,
pre-commit, architecture check, and existing unit/smoke suites.

**Local checks**:

- `python3 tools/codex-harness/validate_active_implementation.py ...`
- `python3 tools/codex-harness/validate_implementation_plan.py ...`
- `python3 tools/codex-harness/validate_workflow_attestations.py --kind owner ...`
- `pre-commit run --all-files`
- `python3 tools/architecture/render.py --check`
- `python3 -m unittest discover -s tools/codex-harness/tests`
- `python3 -m unittest discover -s tools/development/tests`
- `python3 -m unittest discover -s tools/context-pack/tests`
- `uv run --project tools/agent-memory pytest tools/agent-memory/tests`
- `npm ci && npm test` in `tests/smoke`

**Development smoke**: `smoke_profile: none`. This PR does not change cluster
desired state or app behavior.

**Evidence destination**: `specs/sdd-speckit-foundation/evidence.md` and
`.codex/tmp/pr-summary.md`.

## Documentation Impact

Documentation and guidance are the implementation output:

- `AGENTS.md` becomes a shorter router.
- `.specify/memory/constitution.md` records Homelab SDD principles.
- `.specify/templates/` records Homelab artifact guidance.
- `docs/runbooks/spec-driven-development.md` becomes the SDD operating runbook.
- `specs/sdd-speckit-foundation/` records this foundation implementation.

Generated architecture is not expected to change.

## Implementation Steps

1. Create and validate workflow scratch files in the sibling clone.
2. Run Spec Kit initialization with Codex integration.
3. Customize the constitution, SDD templates, and evidence template.
4. Add the SDD runbook.
5. Shorten `AGENTS.md` while preserving critical invariants.
6. Add the foundation spec artifacts.
7. Run requested checks where feasible.
8. Record evidence and PR summary.
9. Commit with a conventional commit.

## Risks

| Risk | Mitigation |
| ---- | ---------- |
| Spec Kit Codex integration is unavailable | Fall back to generic integration and document it in evidence and PR notes |
| Templates conflict with binding ADRs or runbooks | Make ADRs/runbooks authoritative and link them from the constitution and templates |
| Docs-only change skips live validation | Record `smoke_profile: none` with substitute local checks |
| Tooling is unavailable in the clone | Record exact skipped command and reason in evidence and PR summary |

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
| --------- | ---------- | ------------------------------------ |
| N/A | N/A | N/A |
