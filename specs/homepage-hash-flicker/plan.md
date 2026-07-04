# Implementation Plan: Homepage Hash Flicker

**Branch**: `codex/homepage-hash-flicker` | **Date**: 2026-07-04 | **Spec**:
`specs/homepage-hash-flicker/spec.md`

**Input**: Feature specification from
`specs/homepage-hash-flicker/spec.md`

## Summary

Change the shared Homepage Deployment to one replica so a browser session no
longer receives alternating `/api/hash` values from different pods and triggers
Homepage's built-in reload path.

## Technical Context

**Risk Tier**: medium
**Workflow Tier**: medium
**Primary Areas**: Kubernetes app manifest, Spec Kit artifacts
**Dependencies**: kubectl, flux CLI, curl
**Storage**: N/A
**Ingress**: Existing Gateway API HTTPRoute preserved
**Secrets**: No secret changes
**Smoke Strategy**: Existing Homepage development profile if cluster credentials
are available; otherwise render checks plus live curl pre/post evidence
**Fanout Targets**: Render checks and live read-only curl checks are independent
**Development Validation**: Homepage profile when kubeconfig/credentials are
available; otherwise document exception
**Post-Implementation SDD Conformance**: Local repo workflow sources checked

## Constitution Check

*GATE: Must pass before tracked edits and be re-checked before commit.*

- [x] GitOps source of truth preserved; no durable live-cluster-only state.
- [x] No production-first mutation; development validation plan or exception is
      recorded for covered changes.
- [x] Gateway API invariant preserved; no new Kubernetes `Ingress` resources.
- [x] SOPS invariant preserved; no plaintext secret manifests staged.
- [x] NFS default considered for PVC-backed workloads.
- [x] Talos boundary preserved; no SSH-based node operations introduced.
- [x] Branch is `codex/homepage-hash-flicker`; fallback worktree location is
      recorded because `/workspaces/homelab-worktrees` was not writable.
- [x] Documentation impact identified; no canonical docs change expected for a
      replica-count-only fix.
- [x] PR review/status checks are the review gate.

## Project Structure

### SDD Artifacts

```text
specs/homepage-hash-flicker/
├── spec.md
├── plan.md
├── tasks.md
└── evidence.md
```

### Source Or Documentation Changes

```text
kubernetes/apps/homepage/base/deployment.yaml
.specify/feature.json
```

## Tiered TDD And Validation Plan

**TDD expectation**: No new failing unit test is practical for a one-line
Kubernetes manifest change. Use render assertions before and after the edit.

**Local checks**:

- `env -i PATH="$PATH" HOME="$HOME" cluster_domain=lab.petebeegle.com homepage_target_domain=lab.petebeegle.com bash -c 'kubectl kustomize kubernetes/apps/homepage | flux envsubst --strict'`
- `env -i PATH="$PATH" HOME="$HOME" cluster_domain=dev.lab.petebeegle.com homepage_target_domain=lab.petebeegle.com bash -c 'kubectl kustomize kubernetes/apps/homepage/development | flux envsubst --strict'`
- Rendered YAML assertion that both outputs include `replicas: 1` for
  `Deployment/homepage`.

**Development smoke**: Run
`python3 tools/development/verify_branch_deploy.py --app homepage --branch codex/homepage-hash-flicker --slug homepage-hash-flicker --push`
if development kubeconfig and required credentials are available. If not,
record the unavailable-infrastructure exception and substitute local render plus
live curl evidence.

**Automated smoke preference**: For user-facing, routed, deployed, or
operational changes, prefer automated smoke in this order: development branch
profile; production synthetic smoke or one-off in-cluster Job; scriptable
Gateway/DNS/browser smoke against the exact user URL; manual browser checks only
as supplemental evidence.

**Completion evidence**: For deploy follow-up, record source fetched SHA, target
kustomization applied SHA, live resource spec, Gateway/listener match when
applicable, and exact user-facing URL result.

**Fanout plan**: Render checks and read-only curl checks may run independently;
tracked edits remain sequential in the implementation worktree.

**Evidence destination**: `specs/homepage-hash-flicker/evidence.md`.

## Documentation Impact

No canonical docs or generated architecture updates are expected. The behavior
and availability tradeoff are recorded in the implementation artifacts.

## Implementation Steps

1. Bootstrap `specs/homepage-hash-flicker/` artifacts.
2. Change `kubernetes/apps/homepage/base/deployment.yaml` to `replicas: 1`.
3. Render production and development Homepage manifests and assert the replica
   count.
4. Attempt development validation or document the unavailable-infrastructure
   exception.
5. Record evidence and final branch state.

## Risks

| Risk | Mitigation |
| ---- | ---------- |
| Homepage loses one-pod availability during node/pod disruption. | Accept the tradeoff to stop user-facing reloads; PDB remains but can no longer preserve availability during voluntary disruption with one replica. |
| Flicker has another contributing cause. | Render and curl evidence target the verified `/api/hash` reload path; post-deployment hash sampling remains the acceptance check. |
| Development validation cannot run from this environment. | Record the exception and substitute deterministic local renders plus read-only live curl evidence. |

## Complexity Tracking

> Fill only when the constitution check has a violation that must be justified.

| Violation | Why Needed | Simpler Alternative Rejected Because |
| --------- | ---------- | ------------------------------------ |
| N/A | N/A | N/A |
