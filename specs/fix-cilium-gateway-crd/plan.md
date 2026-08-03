# Implementation Plan: Fix Cilium Gateway CRD

**Branch**: `codex/fix-cilium-gateway-crd` | **Date**: 2026-08-03 | **Spec**:
`specs/fix-cilium-gateway-crd/spec.md`

**Input**: Feature specification from
`specs/fix-cilium-gateway-crd/spec.md`

## Summary

Complete the Gateway API v1.5.1 CRD set required by Cilium 1.20.0 by adding the
standard BackendTLSPolicy definition to the shared CRD Kustomization. Validate
the shared cluster base locally and on development, then publish the GitOps
change and verify production controller discovery, certificate synchronization,
TLS routing, telemetry freshness, and alert recovery.

## Technical Context

**Risk Tier**: high
**Workflow Tier**: high
**Primary Areas**: Kubernetes CRDs, Cilium, Gateway API, Flux, production traffic
**Dependencies**: Kustomize, kubectl, Flux, Gateway API v1.5.1, Cilium 1.20.0
**Storage**: N/A
**Ingress**: Existing Cilium Gateway API routes; no route definitions change
**Secrets**: No committed Secret changes; existing certificate Secrets are synced
by Cilium after controller discovery
**Smoke Strategy**: Development `whoami` branch smoke with
`--include-cluster-base`, followed by scriptable production HTTPS and telemetry
checks
**Fanout Targets**: N/A; the work is a single cluster-scoped dependency edit and
multi-agent delegation was not requested
**Development Validation**: `whoami` profile with `--include-cluster-base`
**Post-Implementation SDD Conformance**: Local workflow audit; no upstream
workflow review because this implementation does not change Spec Kit behavior

## Human Gates

**Spec Gate**: Approved by the user through the incident follow-up instruction
"fix" after the diagnosis and repair sequence were presented.

**Checklist Status**: Requirements quality checklist and the 15-item operational
recovery requirements checklist both passed before tasks.

**Plan Gate**: Approved by the same user instruction because the proposed repair
sequence already covered the exact CRD addition, reconciliation, restart, and
recovery checks implemented by this plan.

**Expected Task/Analyze Gate**: Tasks and analysis are required before the source
edit; the user's approval covers implementation if analysis finds no scope or
safety conflict.

## Constitution Check

*GATE: Passed before source edits; re-check before commit.*

- [x] GitOps source of truth preserved; no durable live-cluster-only state.
- [x] No production-first mutation; sequential development validation is planned.
- [x] Gateway API invariant preserved; no Kubernetes `Ingress` resources added.
- [x] SOPS invariant preserved; no plaintext secret manifests staged.
- [x] NFS default considered; no PVC-backed workload is changed.
- [x] Talos boundary preserved; no SSH-based node operations introduced.
- [x] Branch is `codex/fix-cilium-gateway-crd`; the allowed `.codex/tmp`
      fallback worktree is recorded because the preferred sibling directory is
      not writable.
- [x] Documentation impact identified; SDD evidence is sufficient because the
      canonical ingress decision already requires Cilium Gateway API.
- [x] PR review/status checks remain the review gate.

## Project Structure

### SDD Artifacts

```text
specs/fix-cilium-gateway-crd/
├── checklists/
│   ├── requirements.md
│   └── recovery.md
├── contracts/
│   └── gateway-recovery.md
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── tasks.md
└── evidence.md
```

### Source Or Documentation Changes

```text
.specify/feature.json
docs/architecture.md
kubernetes/infra/crds/kustomization.yaml
specs/fix-cilium-gateway-crd/
```

## Tiered TDD And Validation Plan

**TDD expectation**: The pre-change render and both live clusters lack
`backendtlspolicies.gateway.networking.k8s.io`; the production operator logs a
hard prerequisite failure and Envoy has zero certificates. This is the failing
test seam. After the edit, exact render-count assertions and live API discovery
must pass.

**Local checks**:

- `kubectl kustomize kubernetes/infra/crds`
- `kubectl kustomize kubernetes/clusters/development`
- `kubectl kustomize kubernetes/clusters/production`
- Exact count assertion for the BackendTLSPolicy CRD in the shared CRD render
  and for the shared CRD Flux path in each cluster render
- `python3 tools/architecture/render.py --check`
- Repository pre-commit checks for changed files

**Development smoke**: Push the implementation branch and run
`python3 tools/development/verify_branch_deploy.py --app whoami --branch codex/fix-cilium-gateway-crd --slug fix-cilium-gateway-crd --push --include-cluster-base`.
This sequentially applies shared CRDs before Cilium and tests the routed whoami
path. If the operator does not rediscover the newly installed CRD without a
rollout, use a development-only operator restart and record that behavior before
production recovery.

**Automated smoke preference**: The development verifier is primary. Production
verification uses the existing synthetic CronJob plus direct HTTPS checks of
`whoami.lab.petebeegle.com` and `otel.lab.petebeegle.com`.

**Completion evidence**: Record the pushed SHA, merged SHA, Flux-fetched SHA,
`crds` and `cilium` reconciliation state, live CRD, non-empty `cilium-secrets`,
non-empty Envoy certificate output, exact URL results, telemetry sample time,
and active alert list.

**Fanout plan**: None. All outcomes are consolidated into
`specs/fix-cilium-gateway-crd/evidence.md`.

**Evidence destination**: `specs/fix-cilium-gateway-crd/evidence.md`.

## Documentation Impact

No canonical ADR or runbook change is required. Existing documents already say
Gateway API is the ingress contract and Git is the source of truth. The incident
cause, compatibility requirement, rollout behavior, and validation evidence are
durably captured in this implementation's SDD artifacts.

`docs/architecture.md` is regenerated because it inventories each remote shared
CRD resource even though runtime topology is unchanged.

## Implementation Steps

1. Add the Gateway API v1.5.1 standard BackendTLSPolicy CRD URL alongside the
   existing Gateway API resources.
2. Assert the local CRD render contains the resource exactly once, each cluster
   render activates the shared CRD path exactly once, and repository validation
   passes.
3. Commit and push the branch, then run sequential development base and whoami
   smoke validation.
4. Publish through a reviewed PR, wait for Flux to apply the merged source, and
   restart only the Cilium Operator if startup-time discovery requires it.
5. Verify production certificates, HTTPS routes, telemetry freshness, synthetic
   results, and natural alert resolution.

## Risks

| Risk | Mitigation |
| ---- | ---------- |
| A cluster-scoped CRD could conflict with an installed version | Use the same Gateway API v1.5.1 release already selected by the repository and use server-side development validation first. |
| Cilium checks required types only at process start | Prove behavior on development; restart only the operator after the CRD is applied if needed. |
| Development smoke could temporarily affect its shared base | Use the repository's sequential `--include-cluster-base` workflow, which restores the source ref and performs cleanup. |
| Production status may remain stale after the CRD appears | Verify live secret sync, Envoy certificates, and exact HTTPS behavior rather than trusting `Programmed=True` alone. |
| Proxmox hosts could also have an independent outage | Treat restored sample freshness as the telemetry acceptance signal and report any remaining host-level alert separately. |

## Complexity Tracking

No constitution violations or additional complexity are required.
