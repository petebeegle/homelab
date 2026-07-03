# Implementation Plan: sdd-synthetic-smoke-mirroring

**Branch**: `codex/sdd-synthetic-smoke-mirroring` | **Date**: 2026-07-03 | **Spec**:
`specs/sdd-synthetic-smoke-mirroring/spec.md`

**Input**: Feature specification from `specs/sdd-synthetic-smoke-mirroring/spec.md`

## Summary

Sync the shared smoke route spec so local/manual and in-cluster synthetics test
the same route cases, then add a narrow policy command plus pre-commit hook and
unit tests to keep the required mirrored files equal.

## Technical Context

**Risk Tier**: low
**Workflow Tier**: low
**Primary Areas**: Playwright smoke test source, local policy tooling,
pre-commit, runbook documentation
**Dependencies**: Python standard library, unittest, pre-commit, npm,
Playwright smoke package dependencies
**Storage**: N/A
**Ingress**: Gateway API invariant preserved; no route or Gateway manifests are
changed.
**Secrets**: N/A; no secrets are read or touched.
**Development Validation**: none; this is local-only tooling/test-source parity
with no live cluster desired-state change.

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
specs/sdd-synthetic-smoke-mirroring/
├── checklists/
│   └── requirements.md
├── spec.md
├── plan.md
├── tasks.md
└── evidence.md
```

### Source Or Documentation Changes

```text
.pre-commit-config.yaml
docs/runbooks/synthetic-smoke-tests.md
tests/smoke/routes.spec.js
kubernetes/apps/synthetics/smoke/routes.spec.js
tools/policy/check_synthetic_smoke_mirroring.py
tools/policy/tests/test_check_synthetic_smoke_mirroring.py
specs/sdd-synthetic-smoke-mirroring/
```

## Tiered TDD And Validation Plan

**TDD expectation**: Add focused policy unit tests for pass and drift-failure
cases before relying on the new policy command as a guard. The route spec sync is
validated by the policy check and smoke npm tests.

**Local checks**:

- `python3 tools/codex-harness/validate_active_implementation.py --marker .codex/tmp/active-implementation --root "$(pwd)" --branch "$(git branch --show-current)"`
- `python3 tools/codex-harness/validate_implementation_plan.py --plan .codex/tmp/implementation-plan.yaml --marker .codex/tmp/active-implementation --root "$(pwd)" --branch "$(git branch --show-current)"`
- `python3 tools/codex-harness/validate_workflow_attestations.py --kind owner --attestation .codex/tmp/implementation-owner-attestation.yaml --marker .codex/tmp/active-implementation --plan .codex/tmp/implementation-plan.yaml --root "$(pwd)" --branch "$(git branch --show-current)"`
- `python3 -m unittest discover -s tools/policy/tests`
- `python3 -m unittest discover -s tools/development/tests`
- `python3 -m unittest discover -s tools/codex-harness/tests`
- `python3 -m unittest discover -s tools/context-pack/tests`
- `pre-commit run --all-files`
- `python3 tools/architecture/render.py --check`
- `npx -y agnix@0.25.0 .`
- `npm ci && npm test` in `tests/smoke`
- `npm ci && npm test && npm run test:unit` in `kubernetes/apps/synthetics/smoke` when practical
- `uv run --project tools/agent-memory pytest tools/agent-memory/tests`
- `python3 tools/codex-harness/validate_sdd_context.py --marker .codex/tmp/active-implementation --root "$(pwd)" --branch "$(git branch --show-current)" --require-plan-artifacts --require-evidence --head "$(git rev-parse HEAD)"`

**Development smoke**: none. This implementation does not change Kubernetes
desired state beyond smoke source files consumed by the synthetic ConfigMap and
does not change routes, services, Gateway resources, Flux wiring, storage, or
secret references. Local Playwright smoke execution is the substitute check.

**Evidence destination**: `specs/sdd-synthetic-smoke-mirroring/evidence.md` and
`.codex/tmp/pr-summary.md`.

## Documentation Impact

- Update `docs/runbooks/synthetic-smoke-tests.md` to document enforced mirrors
  and intentional exclusions.
- `docs/architecture.md` is expected to remain unchanged; run
  `python3 tools/architecture/render.py --check`.

## Implementation Steps

1. Create workflow files and durable SDD artifacts.
2. Sync `routes.spec.js` from the in-cluster smoke tree into the local/manual
   smoke tree while preserving diagnostics.
3. Add the mirror policy command and focused unit tests.
4. Wire the policy command into pre-commit for mirrored smoke files.
5. Update the synthetic smoke runbook and evidence.
6. Run required validation, clean generated dependency/test output, and commit
   with a conventional message.

## Risks

| Risk | Mitigation |
| ---- | ---------- |
| Future contributors assume all smoke tree files are exact mirrors. | Policy and docs list only the required exact-equality pairs and intentional exclusions. |
| Npm checks generate local dependency or test-output directories. | Remove `node_modules` and test output after validation. |
| Agent-memory check remains blocked by Python 3.14.6 availability. | Record the precise environment limitation if it persists. |

## Complexity Tracking

> Fill only when the constitution check has a violation that must be justified.

| Violation | Why Needed | Simpler Alternative Rejected Because |
| --------- | ---------- | ------------------------------------ |
| N/A | N/A | N/A |
