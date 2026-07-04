# Feature Specification: proxmox-memory-headroom-alert

**Feature Branch**: `codex/proxmox-memory-headroom-alert`
**Created**: 2026-07-03
**Status**: Draft
**Risk Tier**: medium
**Input**: User description: "Implement the approved plan to fix the Proxmox memory alert."

## Summary

Update the existing Proxmox host memory alert so operators are paged only when
actual host memory headroom is low. Fixed VM allocations can keep raw host memory
usage near 90-94%, so the alert should evaluate free GiB and fire below 3 GiB
instead of treating high raw used percentage as actionable by itself.

## Binding Sources

- `AGENTS.md`
- `.specify/memory/constitution.md`
- `docs/runbooks/spec-driven-development.md`
- `docs/runbooks/implementation-workflow.md`
- `docs/decisions/codex-implementation-workflow.md`
- `docs/decisions/tdd-and-development-smoke-evidence.md`

## Scope

### In Scope

- Update only existing Grafana alert rule UID `proxmox-host-memory-high` in
  `kubernetes/infra/monitoring/grafana/alerting/alert-rules-proxmox.yaml`.
- Replace the raw used-percent PromQL with free host memory GiB using:
  `min((proxmox_proxmox_node_memory_memtotal_bytes - proxmox_proxmox_node_memory_memused_bytes) / 1024 / 1024 / 1024)`.
- Remove `OR vector(0)` from this rule.
- Change the threshold evaluator from `gt 90` to `lt 3`.
- Update alert title, summary, description, and runbook annotation to describe
  low Proxmox host memory headroom and explain that 90-94% raw usage from fixed
  VM allocation is not actionable unless free memory falls below 3 GiB.
- Record local checks and read-only production Mimir query observations in
  `specs/proxmox-memory-headroom-alert/evidence.md`.

### Out Of Scope

- Dashboard changes.
- New alert rules, alert routing, notification policy changes, or datasource
  changes.
- Live production Grafana ruler mutation before Flux reconciles merged desired
  state.
- Verifier approval or PR creation by the implementation owner.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Alert On Low Host Headroom (Priority: P1)

Operators need the Proxmox host memory alert to identify genuinely low free host
memory rather than expected high raw allocation percentages.

**Why this priority**: This is the smallest useful change and directly fixes
the noisy or misleading alert condition.

**Independent Test**: Render and validate the alerting kustomization, then query
production Mimir read-only data for the exact pve01 free-memory expression and
the aggregate alert expression.

**Acceptance Scenarios**:

1. **Given** the existing `proxmox-host-memory-high` rule, **When** Grafana
   evaluates the alert expression, **Then** the rule computes free Proxmox host
   memory in GiB and fires only when the aggregate value is below 3 GiB.
2. **Given** pve01 has approximately 90-94% raw memory allocation, **When** free
   host memory remains at or above 3 GiB, **Then** the alert text makes clear
   that raw allocation alone is not actionable.

## Requirements *(mandatory)*

- **FR-001**: The implementation MUST modify only the existing alert rule UID
  `proxmox-host-memory-high` for the behavior change.
- **FR-002**: The rule expression MUST use
  `min((proxmox_proxmox_node_memory_memtotal_bytes - proxmox_proxmox_node_memory_memused_bytes) / 1024 / 1024 / 1024)`,
  with only YAML-equivalent folding changes if needed.
- **FR-003**: The rule expression MUST NOT use `OR vector(0)` for this alert.
- **FR-004**: The threshold evaluator MUST change from greater-than 90 to
  less-than 3.
- **FR-005**: The title, summary, description, and runbook annotation MUST
  describe low Proxmox host memory headroom and clarify that fixed VM allocation
  around 90-94% raw usage is not actionable unless free host memory is below
  3 GiB.
- **FR-006**: Evidence MUST include local YAML/Kubernetes/render checks and
  observed production Mimir values for pve01 free GiB and aggregate alert free
  GiB before any push.
- **FR-007**: Development validation MUST be recorded as not suitable for this
  monitoring/Grafana alerting change, with local render and read-only production
  Mimir query validation as substitute checks.

## Risk And Validation Expectations

This is a medium-risk Kubernetes/Grafana manifest change. TDD is documented as
an exception because the behavior is a declarative alert-rule correction with no
useful failing unit-test seam. Validation uses focused manifest linting,
Kubernetes validation, kustomize rendering, workflow validators, and read-only
production Mimir queries.

## Success Criteria *(mandatory)*

- **SC-001**: `alert-rules-proxmox.yaml` contains the required free-GiB
  aggregate expression and `lt 3` threshold for UID `proxmox-host-memory-high`.
- **SC-002**: `yamllint`, `k8svalidate`, and `kubectl kustomize` checks pass for
  the alerting manifest or overlay.
- **SC-003**: `evidence.md` records observed values for the exact pve01 query and
  aggregate alert query against production Mimir.
- **SC-004**: Workflow marker, plan, owner attestation, and SDD context
  validators pass.

## Assumptions

- Production Mimir can be queried through an available read-only path such as a
  Kubernetes port-forward.
- Flux will reconcile the desired alert manifest after merge; production
  CR/ruler state verification is post-merge and should not be forced with a live
  mutation.

## Open Questions

- None
