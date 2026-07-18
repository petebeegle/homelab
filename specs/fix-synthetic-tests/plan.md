# Implementation Plan: fix-synthetic-tests

**Branch**: `codex/fix-synthetic-tests` | **Date**: 2026-07-17 | **Spec**:
`specs/fix-synthetic-tests/spec.md`

**Input**: Feature specification from `specs/fix-synthetic-tests/spec.md`

## Summary

Retarget the mirrored Homepage synthetic smoke probe from the bare root domain to `homepage.${cluster_domain}`, preserve the intentional subdomain-only route, update stale docs, and validate with mirror, helper, and Playwright checks.

## Technical Context

**Risk Tier**: low
**Workflow Tier**: low
**Primary Areas**: tests, synthetic smoke tooling, docs
**Dependencies**: Python unittest, Node.js/npm, Playwright smoke package, architecture renderer
**Storage**: N/A
**Ingress**: No desired-state ingress changes
**Secrets**: N/A
**Smoke Strategy**: local Playwright smoke against configured `SMOKE_BASE_DOMAIN`
**Fanout Targets**: read-only inspection and independent local validation commands
**Development Validation**: none; final change is test/docs only
**Post-Implementation SDD Conformance**: local docs only

## Human Gates

**Spec Gate**: approved by user request and follow-up correction.

**Checklist Status**: skipped; low-risk focused repair with concrete failing checks.

**Plan Gate**: approved by user request to proceed with the fix.

**Expected Task/Analyze Gate**: analyze skipped with rationale in evidence; tasks are small and directly executable.

## Constitution Check

*GATE: Must pass before tracked edits and be re-checked before commit.*

- [x] GitOps source of truth preserved; no durable live-cluster-only state.
- [x] No production-first mutation; no desired-state cluster change in final scope.
- [x] Gateway API invariant preserved; no new Kubernetes `Ingress` resources.
- [x] SOPS invariant preserved; no plaintext secret manifests staged.
- [x] NFS default considered for PVC-backed workloads.
- [x] Talos boundary preserved; no SSH-based node operations introduced.
- [x] Branch is `codex/fix-synthetic-tests`; fallback worktree mode is recorded in evidence.
- [x] Documentation impact identified; stale smoke docs updated.
- [x] PR review/status checks are the review gate.

## Project Structure

### SDD Artifacts

```text
specs/fix-synthetic-tests/
├── spec.md
├── plan.md
├── tasks.md
└── evidence.md
```

### Source Or Documentation Changes

```text
tests/smoke/routes.spec.js
kubernetes/apps/synthetics/smoke/routes.spec.js
docs/runbooks/synthetic-smoke-tests.md
kubernetes/apps/homepage/README.md
```

## Tiered TDD And Validation Plan

**TDD expectation**: Reproduce the failing root-domain Homepage smoke check, then fix the test target without changing routing.

**Local checks**:

- `python3 tools/policy/check_synthetic_smoke_mirroring.py`
- `python3 -m unittest tools.policy.tests.test_check_synthetic_smoke_mirroring`
- `node --test kubernetes/apps/synthetics/smoke/*.test.js`
- `npm test -- --reporter=list`
- `python3 tools/architecture/render.py --check`

**Development smoke**: none; no Kubernetes desired-state or app behavior change is planned.

**Automated smoke preference**: Local Playwright smoke is the strongest practical check for this low-risk test repair.

**Completion evidence**: Record command outcomes and final PR state.

**Fanout plan**: Independent policy/helper validations may run in parallel after edits; all results are recorded in one evidence file.

**Evidence destination**: `specs/fix-synthetic-tests/evidence.md`.

## Documentation Impact

Update stale smoke and Homepage docs to identify `homepage.${cluster_domain}` as the intended dashboard URL.

## Implementation Steps

1. Reproduce failing synthetic tests locally.
2. Retarget the Homepage smoke probe in both mirrored route spec files.
3. Update stale docs that described the root-domain Homepage target.
4. Run focused validation and record evidence.

## Risks

| Risk | Mitigation |
| ---- | ---------- |
| Mirrored route specs drift | Run mirror policy check after edits. |
| Docs continue to imply a root route | Update smoke runbook and Homepage README with subdomain target. |

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
| --------- | ---------- | ------------------------------------ |
| N/A | N/A | N/A |
