# Implementation Plan: sdd-dev-smoke-matrix

**Branch**: `codex/sdd-dev-smoke-matrix` | **Date**: 2026-07-03 | **Spec**:
`specs/sdd-dev-smoke-matrix/spec.md`

**Input**: Feature specification from
`specs/sdd-dev-smoke-matrix/spec.md`

## Summary

Extend the existing config-driven development smoke verifier rather than adding
production synthetic smoke as the first proof. The slice will add generic profile
fields and checker steps, preserve current app behavior, add safe app coverage
where manifests can be isolated by branch slug, and document coverage gaps for
apps that require secrets, shared dependencies, or larger refactors.

## Technical Context

**Risk Tier**: medium
**Workflow Tier**: medium
**Primary Areas**: Python smoke tooling, Kubernetes branch overlays, Gateway API
routes, secret references, docs, SDD evidence
**Dependencies**: Python unittest, kubectl command wrappers, Flux CRDs, Gateway
API CRDs, pre-commit, agnix, npm smoke tests when applicable
**Storage**: Branch PVC checks must preserve `nfs-csi-storage` expectations
**Ingress**: Gateway API `HTTPRoute` and `TLSRoute`; no Kubernetes `Ingress`
**Secrets**: Check only Secret object existence by referenced names; do not
inspect, decrypt, or log Secret data
**Development Validation**: Attempt `whoami` profile against
`codex/sdd-dev-smoke-matrix` with slug `sdd-dev-smoke-matrix` only if
development cluster credentials are available and safe; otherwise record an
unavailable-infrastructure exception

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
specs/sdd-dev-smoke-matrix/
├── checklists/
│   └── smoke-readiness.md
├── spec.md
├── plan.md
├── tasks.md
└── evidence.md
```

### Source Or Documentation Changes

```text
tools/development/devverify/config.py
tools/development/devverify/profiles.py
tools/development/devverify/checks.py
tools/development/devverify/cleanup.py
tools/development/devverify/flux.py
tools/development/devverify/workflow.py
tools/development/devverify/cli.py
tools/development/tests/test_verify_branch_deploy.py
tools/development/smoke-profiles/*.json
kubernetes/clusters/development/branches/*
kubernetes/apps/pihole/branch/*
kubernetes/apps/foundryvtt/branch/*
docs/runbooks/development-cluster.md
tools/development/README.md
tests/smoke
kubernetes/apps/synthetics/smoke
```

## Tiered TDD And Validation Plan

**TDD expectation**: Add or update focused unit tests for schema parsing,
checker execution, cleanup behavior, and command sequencing before or alongside
implementation. Record any red-test command that cannot be isolated.

**Local checks**:

- `python3 -m unittest discover -s tools/development/tests`
- `python3 -m unittest discover -s tools/codex-harness/tests`
- `python3 -m unittest discover -s tools/context-pack/tests`
- `pre-commit run --all-files`
- `python3 tools/architecture/render.py --check`
- `npx -y agnix@0.25.0 .`
- `npm ci && npm test` in `tests/smoke` if touched or quick
- `uv run --project tools/agent-memory pytest tools/agent-memory/tests`

**Development smoke**: Attempt
`python3 tools/development/verify_branch_deploy.py --app whoami --branch codex/sdd-dev-smoke-matrix --slug sdd-dev-smoke-matrix --push`
only if development kubeconfig and credentials are available and safe. Use
`--include-cluster-base` only if shared base resources change.

**Evidence destination**: `specs/sdd-dev-smoke-matrix/evidence.md` and
`.codex/tmp/pr-summary.md`.

## Documentation Impact

- Update `docs/runbooks/development-cluster.md` with profile coverage, route URL
  and Playwright handoff, app gaps, and live validation exception guidance.
- Update `tools/development/README.md` with new schema fields and profile
  examples.
- Update `docs/architecture.md` only if Kubernetes/Terraform source changes
  affect generated architecture output.

## Implementation Steps

1. Inspect existing devverify code, tests, profiles, app manifests, branch
   overlays, synthetic smoke sources, and development docs.
2. Add focused tests for the new schema/checks and command sequencing.
3. Implement profile parsing and checker support for Kustomizations, TLSRoutes,
   Secret references, and route URLs while preserving existing behavior.
4. Add safe smoke profiles and branch overlays for `pihole` and/or
   `foundryvtt`; document gaps for `authentik` and `monitoring`.
5. Audit synthetic smoke duplication and implement a mirror check only if small
   and safe; otherwise document the follow-up.
6. Run required validation, update evidence, commit, and stop before PR creation.

## Risks

| Risk | Mitigation |
| ---- | ---------- |
| Secret checks accidentally reveal data | Only call metadata/existence checks by Secret name and avoid printing payloads |
| App overlays collide with production | Require branch slug in names, hostnames, and generated resources |
| Complex apps exceed slice size | Document exact gap and leave follow-up instead of broad refactors |
| Development credentials unavailable | Record exception and run unit/static/render checks |

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
| --------- | ---------- | ------------------------------------ |
| N/A | N/A | N/A |
