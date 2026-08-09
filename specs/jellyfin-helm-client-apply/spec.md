# Feature Specification: Jellyfin Helm Client Apply

**Feature Branch**: `codex/jellyfin-helm-client-apply`
**Created**: 2026-08-09
**Status**: Approved
**Risk Tier**: medium
**Input**: Continue iterating on the Jellyfin migration until production
success, deferring cleanup until every binding acceptance gate passes.

## Human Gate Status

**Intent Brief**: Make the approved recreate transition remove API-defaulted
rolling-update state without a live mutation or resource replacement.

**Clarify Status**: Skipped. Managed fields and a server-side dry-run of the
client-style strategic patch identify the exact apply-mode mismatch.

**Spec Gate**: Approved by the user's instruction to keep going.

## Summary

Use an apply mode that can remove the live Deployment's API-defaulted
rolling-update configuration during the transition to recreate. Apply the same
mode to rollback so failure recovery remains consistent, while preserving all
migration, storage, authentication, GPU, and route behavior.

## Binding Sources

- `AGENTS.md`
- `.specify/memory/constitution.md`
- `docs/runbooks/implementation-workflow.md`
- `docs/decisions/jellyfin-local-config-storage.md`
- `docs/runbooks/jellyfin-authentik-sso.md`

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Strategy transition applies (Priority: P1)

As the operator, I can apply the recreate transition with an update method that
removes API-defaulted rolling settings instead of retaining an invalid field.

**Independent Test**: Render the full Jellyfin desired state and verify both
upgrade and rollback explicitly select the compatible apply mode.

**Acceptance Scenarios**:

1. **Given** the live field is defaulted and unowned by the current server-side
   manager, **When** the repaired upgrade runs, **Then** the strategic update
   removes it and Kubernetes accepts recreate.
2. **Given** a later migration failure, **When** Helm rolls back, **Then** rollback
   uses the same declared apply mode and can restore the previous release.

### User Story 2 - Cutover safety remains gated (Priority: P1)

As a Jellyfin user or administrator, I retain the approved migration and
identity safeguards and continue receiving service until a valid cutover starts.

**Independent Test**: Existing focused migration and render assertions all pass,
and the implementation diff changes only Helm action behavior plus tests/SDD.

**Acceptance Scenarios**:

1. **Given** the repaired release, **When** it renders, **Then** storage, init
   ordering, GPU, authentication, routes, and rollback source are unchanged.
2. **Given** production technical success, **When** cleanup is considered,
   **Then** unverified authenticated acceptance still prevents cleanup.

## Edge Cases

- Replacement forcing is ineffective while server-side apply is active and is
  unnecessary when the strategic patch already succeeds.
- Rollback may occur after the old Deployment is removed; its apply mode must be
  declared rather than inherited from release history.
- Pod readiness and anonymous SSO redirects do not prove user/admin access.

## Requirements *(mandatory)*

- **FR-001**: Jellyfin Helm upgrades MUST explicitly use client-side apply for
  this transition.
- **FR-002**: Jellyfin Helm rollbacks MUST explicitly use the same apply mode.
- **FR-003**: The repair MUST NOT enable force replacement.
- **FR-004**: The full rendered desired state MUST contain both apply-mode
  declarations and the existing recreate/null strategy intent.
- **FR-005**: Existing migration behavior and storage, GPU, authentication,
  route, and resource invariants MUST remain unchanged.
- **FR-006**: Production verification MUST cover revision, Helm, workload,
  migration, storage, logs, and exact user paths before cleanup is considered.

## Success Criteria *(mandatory)*

- **SC-001**: Focused regression fails at the merged baseline and passes with
  both action modes declared.
- **SC-002**: All existing Jellyfin migration and render tests pass.
- **SC-003**: Production Helm upgrade completes without the strategy validation
  error or a force replacement setting.
- **SC-004**: Migration runs successfully and Jellyfin serves from the local
  claim while the NFS rollback claim remains retained.
- **SC-005**: Web and SSO-start paths remain healthy, with authenticated
  acceptance limitations stated before cleanup.

## Assumptions

- Helm controller's disabled server-side mode uses the strategic client-side
  patch behavior verified by the read-only API dry-run.
- The old application remains safely restored after the failed prior rollout.

## Open Questions

- None.
