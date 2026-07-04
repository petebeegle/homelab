# Implementation Plan: proxmox-memory-headroom-alert

**Branch**: `codex/proxmox-memory-headroom-alert` | **Date**: 2026-07-03 |
**Spec**: `specs/proxmox-memory-headroom-alert/spec.md`

**Input**: Feature specification from
`specs/proxmox-memory-headroom-alert/spec.md`

## Summary

Change the existing Proxmox host memory Grafana rule from a raw used-percent
threshold to a free-memory headroom threshold. The alert will evaluate the
minimum free host memory in GiB across Proxmox nodes and fire below 3 GiB, with
operator-facing text explaining that expected 90-94% fixed VM allocation is not
actionable by itself.

## Technical Context

**Risk Tier**: medium
**Workflow Tier**: medium
**Primary Areas**: Kubernetes manifests, Grafana alerting, monitoring
**Dependencies**: Flux, Grafana alerting provisioning, Mimir metrics, kubectl,
pre-commit
**Storage**: N/A
**Ingress**: N/A
**Secrets**: No secret manifests changed
**Development Validation**: none with reason: the development branch verifier is
not suitable for monitoring/Grafana alerting semantics that depend on production
Proxmox metrics; substitute local render/schema checks plus read-only production
Mimir query validation.

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
- [x] Documentation impact identified; no-docs rationale recorded.
- [x] Separate verifier approval required before PR creation.

## Project Structure

### SDD Artifacts

```text
specs/proxmox-memory-headroom-alert/
├── spec.md
├── plan.md
├── tasks.md
└── evidence.md
```

### Source Or Documentation Changes

```text
kubernetes/infra/monitoring/grafana/alerting/alert-rules-proxmox.yaml
specs/proxmox-memory-headroom-alert/spec.md
specs/proxmox-memory-headroom-alert/plan.md
specs/proxmox-memory-headroom-alert/tasks.md
specs/proxmox-memory-headroom-alert/evidence.md
```

## Tiered TDD And Validation Plan

**TDD expectation**: Documented exception. This is a narrow declarative Grafana
alert-rule correction, and the repository has no practical failing unit-test seam
for the intended PromQL semantics. Use focused render/schema validation and
read-only Mimir query checks instead.

**Local checks**:

- `pre-commit run yamllint --files kubernetes/infra/monitoring/grafana/alerting/alert-rules-proxmox.yaml`
- `pre-commit run k8svalidate --files kubernetes/infra/monitoring/grafana/alerting/alert-rules-proxmox.yaml`
- `kubectl kustomize kubernetes/infra/monitoring/grafana/alerting >/tmp/proxmox-alerting-render.yaml`
- `python3 tools/codex-harness/validate_active_implementation.py --marker .codex/tmp/active-implementation --root "$(pwd)" --branch "$(git branch --show-current)"`
- `python3 tools/codex-harness/validate_implementation_plan.py --plan .codex/tmp/implementation-plan.yaml --marker .codex/tmp/active-implementation --root "$(pwd)" --branch "$(git branch --show-current)"`
- `python3 tools/codex-harness/validate_workflow_attestations.py --kind owner --attestation .codex/tmp/implementation-owner-attestation.yaml --marker .codex/tmp/active-implementation --plan .codex/tmp/implementation-plan.yaml --root "$(pwd)" --branch "$(git branch --show-current)"`
- `python3 tools/codex-harness/validate_sdd_context.py --marker .codex/tmp/active-implementation --root "$(pwd)" --branch "$(git branch --show-current)" --require-plan-artifacts`
- `python3 tools/codex-harness/validate_sdd_context.py --marker .codex/tmp/active-implementation --root "$(pwd)" --branch "$(git branch --show-current)" --require-plan-artifacts --require-evidence --head "$(git rev-parse HEAD)"`

**Development smoke**: none. The development branch verifier does not validate
production Proxmox memory metrics or Grafana alert evaluation semantics for this
rule. Substitute checks are local render/schema validation plus read-only
production Mimir queries:

- `(proxmox_proxmox_node_memory_memtotal_bytes{proxmox_node="pve01"} - proxmox_proxmox_node_memory_memused_bytes{proxmox_node="pve01"}) / 1024 / 1024 / 1024`
- `min((proxmox_proxmox_node_memory_memtotal_bytes - proxmox_proxmox_node_memory_memused_bytes) / 1024 / 1024 / 1024)`

**Evidence destination**: `specs/proxmox-memory-headroom-alert/evidence.md` and
`.codex/tmp/pr-summary.md`.

## Documentation Impact

No separate runbook, ADR, generated architecture, or dashboard update is needed.
The operator-facing alert annotations are the documentation surface changed by
this implementation.

## Implementation Steps

1. Validate workflow owner marker, implementation plan, and owner attestation.
2. Create SDD artifacts and validate SDD context.
3. Update only UID `proxmox-host-memory-high` in the Proxmox alert rules
   manifest.
4. Run local validators and kustomize render.
5. Query production Mimir read-only data for pve01 and aggregate free GiB.
6. Record all outcomes, final HEAD, and development validation exception in
   evidence and PR summary.
7. Commit with a conventional commit message and stop before verifier approval,
   push, or PR creation.

## Risks

| Risk | Mitigation |
| ---- | ---------- |
| PromQL folding changes expression semantics | Preserve the exact aggregate expression aside from YAML folding. |
| Development validation cannot represent production Proxmox metrics | Record exception and substitute read-only production Mimir query evidence. |
| Production ruler state cannot be verified before Flux merge | Leave post-merge validation note and do not mutate production. |

## Complexity Tracking

> Fill only when the constitution check has a violation that must be justified.

| Violation | Why Needed | Simpler Alternative Rejected Because |
| --------- | ---------- | ------------------------------------ |
| N/A | N/A | N/A |
