# Recovery Requirements Checklist: Fix Cilium Gateway CRD

**Purpose**: Review the completeness, clarity, consistency, and measurability of
the cluster recovery requirements before implementation
**Created**: 2026-08-03
**Feature**: [spec.md](../spec.md)

**Note**: This checklist reviews requirements quality, not implementation state.

## Requirement Completeness

- [x] CHK001 Are requirements present for both durable desired state and one-time
  operational recovery actions? [Completeness, Spec §FR-001, §Assumptions]
- [x] CHK002 Are the development and production validation layers both specified?
  [Completeness, Spec §FR-004–FR-007]
- [x] CHK003 Are requirements defined for user-facing routing, controller state,
  certificate synchronization, telemetry freshness, and alert recovery?
  [Completeness, Spec §SC-002–SC-005]

## Requirement Clarity

- [x] CHK004 Is the required API surface named unambiguously without implying a
  broader Gateway API upgrade? [Clarity, Spec §Scope, §FR-001]
- [x] CHK005 Is "recovery" clarified as an HTTP/TLS user-path outcome rather than
  resource readiness alone? [Clarity, Spec §FR-006–FR-007]
- [x] CHK006 Is the permitted live action bounded to startup-time operator
  discovery rather than general data-plane restarts? [Clarity, Spec §Assumptions]

## Requirement Consistency

- [x] CHK007 Do the recovery requirements align with the GitOps invariant while
  allowing documented one-time operational recovery? [Consistency, Spec §FR-002]
- [x] CHK008 Do the no-route-change and no-alert-change boundaries align with all
  success criteria? [Consistency, Spec §FR-003, §SC-005]
- [x] CHK009 Are development-first requirements consistent with the production
  verification sequence? [Consistency, Spec §FR-005–FR-006]

## Acceptance Criteria Quality

- [x] CHK010 Can the exact rendered CRD count be objectively measured for both
  cluster entrypoints? [Measurability, Spec §SC-001]
- [x] CHK011 Are HTTPS success criteria measurable without relying on stale
  Gateway status? [Measurability, Spec §SC-002–SC-003]
- [x] CHK012 Is telemetry recovery bounded by a concrete sampling interval?
  [Measurability, Spec §SC-004]

## Scenario And Edge-Case Coverage

- [x] CHK013 Is the missing startup rediscovery path addressed without requiring
  unnecessary agent or Envoy restarts? [Recovery Coverage, Spec §Assumptions]
- [x] CHK014 Is a possible independent Proxmox outage separated from restoration
  of the telemetry transport? [Exception Coverage, Spec §SC-004–SC-005]
- [x] CHK015 Are unavailable-development-infrastructure requirements defined
  without allowing an actual failed validation to be waived? [Edge Case,
  Spec §FR-005]

## Notes

- Standard-depth checklist for author and PR reviewer use.
- Focus areas: cluster-scoped compatibility, recovery sequencing, observable
  acceptance, and false-positive versus independent-alert boundaries.
- All 15 requirements-quality checks passed before task generation.
