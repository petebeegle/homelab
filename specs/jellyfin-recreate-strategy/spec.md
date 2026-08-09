# Feature Specification: Jellyfin Recreate Strategy

**Feature Branch**: `codex/jellyfin-recreate-strategy`
**Created**: 2026-08-09
**Status**: Approved
**Risk Tier**: medium
**Input**: Continue iterating on the merged Jellyfin migration until production
success; clean up migration assets only after success.

## Human Gate Status

**Intent Brief**: Repair the production rollout transition without weakening
the already-approved storage migration, authentication, rollback, GPU, or
availability constraints.

**Clarify Status**: Skipped. Production events and chart rendering identify one
exact invalid transition: a stale rolling-update configuration remains when the
workload changes to a recreate strategy.

**Spec Gate**: Approved by the user's explicit instruction to keep going and
iterate as needed.

## Summary

Allow the Jellyfin migration rollout to replace the existing rolling-update
strategy with a recreate strategy. The desired state must explicitly remove the
strategy setting that is invalid under recreate, while preserving every other
migration, storage, authentication, GPU, and rollback safeguard.

## Binding Sources

- `AGENTS.md`
- `.specify/memory/constitution.md`
- `docs/runbooks/implementation-workflow.md`
- `docs/runbooks/spec-driven-development.md`
- `docs/decisions/jellyfin-local-config-storage.md`
- `docs/decisions/tdd-and-development-smoke-evidence.md`
- `docs/runbooks/jellyfin-authentik-sso.md`

## Scope

### In Scope

- Make the rolling-to-recreate workload transition valid for the existing live
  deployment.
- Add regression coverage for the rendered strategy transition.
- Preserve the full local-config migration and its rollback source.
- Verify the repaired revision through review checks and layered production
  acceptance.

### Out Of Scope

- Changing storage classes, PVC names, migration integrity rules, GPU pinning,
  authentication configuration, routes, or resource limits.
- Applying missing development GPU/VM infrastructure.
- Removing migration assets before the repaired production migration and
  authentication acceptance gates succeed.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Valid migration rollout (Priority: P1)

As the operator, I can roll Jellyfin from its existing update strategy to the
required single-writer migration strategy without Kubernetes rejecting the
workload.

**Why this priority**: The current upgrade is rolled back before any migration
pod can start.

**Independent Test**: Render the exact Jellyfin release and verify that the
recreate strategy also removes the incompatible rolling-update setting.

**Acceptance Scenarios**:

1. **Given** the live workload still carries rolling-update configuration,
   **When** the repaired release is applied, **Then** the strategy transition is
   accepted and the migration pod can start.
2. **Given** the repaired desired state, **When** it is rendered, **Then** it
   explicitly removes the incompatible setting rather than relying on implicit
   field deletion.

### User Story 2 - Migration safeguards remain intact (Priority: P1)

As a Jellyfin user or administrator, I retain the approved config migration,
SSO, storage, rollback, and scheduling safeguards while the transition is
repaired.

**Why this priority**: A rollout repair must not change the data or identity
contract.

**Independent Test**: Compare the rendered claims, init order, resources,
selection, and authentication references with the approved migration design.

**Acceptance Scenarios**:

1. **Given** the repaired release, **When** it renders, **Then** the local target,
   read-only NFS source, migration-before-SSO ordering, GPU selection, and
   authentication references are unchanged.
2. **Given** production rollout succeeds, **When** acceptance is evaluated,
   **Then** migration cleanup remains gated on storage, application, and
   authentication evidence rather than readiness alone.

## Edge Cases

- Helm rollback may leave the old deployment healthy while the new local claim
  remains pending; this is safe pre-migration state, not success.
- A null/clear operation must survive the chart render and reach the deployment
  patch rather than disappearing from the desired state.
- A completed technical migration does not by itself prove authenticated user,
  administrator, or native-login acceptance.

## Requirements *(mandatory)*

- **FR-001**: Desired state MUST explicitly clear the rolling-update setting
  while selecting the recreate strategy.
- **FR-002**: The exact release render MUST contain a valid clear operation and
  recreate strategy together.
- **FR-003**: The repair MUST NOT change PVCs, storage classes, init ordering,
  migration logic, GPU selection, authentication settings, routes, or resource
  limits.
- **FR-004**: Automated regression coverage MUST fail when the incompatible
  rolling-update field is not explicitly cleared.
- **FR-005**: Production verification MUST distinguish merged, fetched, applied,
  live workload, migration, storage, and user-path layers.
- **FR-006**: Migration cleanup MUST remain deferred until all binding cutover
  acceptance gates that can safely authorize cleanup are satisfied.

## Success Criteria *(mandatory)*

- **SC-001**: The repaired release renders exactly one recreate strategy with
  the incompatible rolling-update setting explicitly cleared.
- **SC-002**: All focused migration and strategy regression tests pass.
- **SC-003**: Production accepts the repaired workload and completes the
  migration init sequence without rollback.
- **SC-004**: The live application uses the local config claim while the old NFS
  claim remains retained for immediate rollback.
- **SC-005**: Exact web and SSO-start paths remain healthy after rollout, with
  any authenticated acceptance limitation stated explicitly.

## Assumptions

- The chart renders a null strategy value as an explicit field-clear operation.
- The existing rollback preserved the pre-migration workload and NFS config.
- The known development GPU limitation remains out of scope by user direction.

## Open Questions

- None.
