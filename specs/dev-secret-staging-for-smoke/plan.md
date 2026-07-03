# Implementation Plan: dev-secret-staging-for-smoke

**Branch**: `codex/dev-secret-staging-for-smoke` | **Date**: 2026-07-03 |
**Spec**: `specs/dev-secret-staging-for-smoke/spec.md`

**Input**: Feature specification from
`specs/dev-secret-staging-for-smoke/spec.md`

## Summary

Add a focused shell wrapper around the existing secret staging and installation
scripts so development smoke prerequisites are installed into implementation and
verifier clones consistently before live branch validation.

## Technical Context

**Risk Tier**: low
**Workflow Tier**: low
**Primary Areas**: Codex scripts, local tooling tests, runbooks
**Dependencies**: Bash, Git, Python unittest
**Storage**: N/A
**Ingress**: N/A
**Secrets**: Copies ignored local Terraform tfvars by path only; no values are
printed or committed
**Development Validation**: none; local tooling/docs only

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
specs/dev-secret-staging-for-smoke/
├── spec.md
├── plan.md
├── tasks.md
└── evidence.md
```

### Source Or Documentation Changes

```text
.codex/scripts/prepare_development_smoke_secrets.sh
tools/codex-harness/tests/test_prepare_development_smoke_secrets.py
docs/runbooks/implementation-workflow.md
docs/runbooks/development-cluster.md
tools/development/README.md
```

## Tiered TDD And Validation Plan

**TDD expectation**: Add focused unit tests for the wrapper behavior.

**Local checks**:

- `python3 -m unittest tools.codex-harness.tests.test_prepare_development_smoke_secrets`
- `python3 -m unittest discover -s tools/codex-harness/tests`
- `bash -n .codex/scripts/*.sh`
- `pre-commit run --all-files`

**Development smoke**: none. The change helps prepare live smoke but does not
change cluster behavior.

**Evidence destination**: `specs/dev-secret-staging-for-smoke/evidence.md` and
`.codex/tmp/pr-summary.md`.

## Documentation Impact

Update workflow and development validation docs so operators run the wrapper
before smoke commands that perform Terraform preflight.

## Implementation Steps

1. Add failing unit tests for required wrapper behavior.
2. Add `.codex/scripts/prepare_development_smoke_secrets.sh`.
3. Update docs with the standard pre-smoke command.
4. Run focused tests, harness tests, shell syntax checks, and pre-commit.
5. Record evidence and commit.

## Risks

| Risk | Mitigation |
| ---- | ---------- |
| Secret values are exposed | Print paths/counts only; tests assert behavior without real secrets |
| Unsafe tfvars source is copied | Refuse missing, tracked, and non-ignored sources before staging |
| Verifier clone misses inputs | Support one or more clone paths in a single command |

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
| --------- | ---------- | ------------------------------------ |
| N/A | N/A | N/A |
