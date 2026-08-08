# Feature Specification: jellyfin-local-config

**Feature Branch**: `codex/jellyfin-local-config`
**Created**: 2026-08-08
**Status**: Approved
**Risk Tier**: medium
**Input**: User description: "Jellyfin seems to really struggle whenever I'm adding new media"; preserve authentication and account for low cluster memory.

## Human Gate Status

**Intent Brief**: Reduce Jellyfin degradation during media ingestion by moving
latency-sensitive `/config` I/O off Synology NFS. Preserve all existing
authentication, users, permissions, plugins, metadata, and a native administrator
recovery path. Keep media on Synology. Fail closed on partial migration. Treat
low-memory conditions as a cutover gate rather than increasing steady-state
memory reservations.

**Clarify Status**: Run through the conversation. The user explicitly elevated
authentication preservation to a critical constraint and asked whether the
cluster memory warning changes the design.

**Spec Gate**: Approved by Pete after reviewing the proposed artifacts and
authentication/memory safeguards; "Ok let's open the PR" authorizes the bounded
implementation.

## Summary

Move Jellyfin's live configuration and database state from its NFS-backed PVC to
a node-local PVC so library scans and media ingestion do not perform
latency-sensitive config I/O over NFS. Preserve the entire existing config tree,
run a validated one-time migration before Jellyfin starts, retain the old NFS
PVC for immediate rollback, and leave Authentik configuration and secrets
unchanged.

## Binding Sources

- `AGENTS.md`
- `.specify/memory/constitution.md`
- `docs/runbooks/implementation-workflow.md`
- `docs/runbooks/spec-driven-development.md`
- `docs/decisions/synology-nfs-storage.md`
- `docs/decisions/tdd-and-development-smoke-evidence.md`
- `docs/runbooks/jellyfin-authentik-sso.md`

## Scope

### In Scope

- Add a `local-path` PVC for Jellyfin `/config`.
- Preserve the existing NFS config PVC as a read-only migration and immediate
  rollback source.
- Copy and validate the complete Jellyfin config tree before application
  startup.
- Preserve existing local accounts, user identifiers, permissions,
  administrator assignments, plugins, SSO configuration, branding, and database
  state.
- Use `Recreate` so the source database is quiescent during copy.
- Bound migration and SSO init-container resources.
- Add an app-specific binding storage decision and operational runbook guidance.
- Add a focused executable test for migration success, retry, and fail-closed
  behavior.

### Out Of Scope

- Moving the media library off Synology.
- Changing the Authentik application, provider, redirect URI, client ID, client
  secret, scopes, group names, or role mappings.
- Disabling native Jellyfin login.
- Changing Jellyfin chapter-image, trickplay, or scan-parallelism settings.
- Making `local-path` highly available.
- Automating backup or replication of the new local volume.
- Changing Jellyfin's main-container memory request or limit.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Responsive media ingestion (Priority: P1)

As a Jellyfin user, I can continue browsing or playing media while new content is
being discovered without Jellyfin's database and metadata writes competing on
the NFS config volume.

**Why this priority**: This is the reported operational problem and the smallest
valuable outcome.

**Independent Test**: Render the workload and confirm `/config` uses
`jellyfin-config-local-v1` with StorageClass `local-path`, while
`/custom-media` remains the Synology NFS mount.

**Acceptance Scenarios**:

1. **Given** the existing NFS-backed config and Synology media library, **When**
   the migration rollout completes, **Then** Jellyfin reads and writes `/config`
   on the local PVC and continues to read media from Synology.
2. **Given** a subsequent library scan, **When** Jellyfin updates its databases
   and metadata, **Then** those config operations no longer target
   `jellyfin-config-v2`.

### User Story 2 - Authentication survives cutover (Priority: P1)

As an existing user or administrator, I can sign in through the same Authentik
identity and retain the same Jellyfin account and privileges after migration,
while a native administrator remains available for recovery.

**Why this priority**: Authentication loss would make the performance fix
unacceptable and could lock out administration.

**Independent Test**: The migration test proves all database files and pinned SSO
artifacts are copied and byte-matched before the completion marker. Cutover
acceptance then verifies an existing user, existing SSO administrator, and native
administrator.

**Acceptance Scenarios**:

1. **Given** an existing `Jellyfin Users` member, **When** they complete OIDC
   login after cutover, **Then** they reach their existing Jellyfin account.
2. **Given** an existing `Jellyfin Admins` member, **When** they sign in, **Then**
   administrator access remains.
3. **Given** Authentik is unavailable, **When** a known local administrator uses
   native login, **Then** recovery access remains possible.
4. **Given** a missing database, SSO config, branding file, or plugin artifact,
   **When** migration runs, **Then** Jellyfin does not start.

### User Story 3 - Safe retry and rollback (Priority: P2)

As the cluster operator, I can retry an interrupted migration and immediately
roll back without modifying the original NFS config.

**Why this priority**: Local storage introduces node affinity and the cluster is
already warning about low memory, so cutover must fail safely.

**Independent Test**: The migration test starts with an untrusted partial target,
verifies it is replaced, verifies the completion marker, and verifies a completed
target can be validated on restart without recopying source data.

**Acceptance Scenarios**:

1. **Given** an interrupted target without the completion marker, **When** the
   init container retries, **Then** it clears the target and recopies from the
   read-only source.
2. **Given** a completed migration, **When** the pod restarts, **Then** the target
   is validated and the copy is skipped.
3. **Given** the selected iGPU worker reports `MemoryPressure=True`, **When**
   cutover is evaluated, **Then** deployment acceptance remains blocked.
4. **Given** authentication acceptance fails, **When** rollback is chosen,
   **Then** GitOps can point `/config` back to the retained NFS PVC.

## Requirements *(mandatory)*

- **FR-001**: Jellyfin `/config` MUST use a PVC named
  `jellyfin-config-local-v1` with StorageClass `local-path`.
- **FR-002**: `/custom-media` MUST remain mounted from
  `/volume1/Media/Jellyfin` on Synology NFS.
- **FR-003**: `jellyfin-config-v2` MUST remain declared and MUST be mounted
  read-only by the migration container.
- **FR-004**: The Deployment MUST use `Recreate`.
- **FR-005**: Migration MUST run before the existing SSO bootstrap and before the
  Jellyfin container.
- **FR-006**: Migration MUST copy the complete config tree, including hidden
  files.
- **FR-007**: Migration MUST validate a non-empty Jellyfin database plus
  `system.xml`, `branding.xml`, `SSO-Auth.xml`, and all expected pinned SSO plugin
  files.
- **FR-008**: Migration MUST byte-compare the copied database files and critical
  authentication artifacts before writing its completion marker.
- **FR-009**: A target without the completion marker MUST be treated as
  incomplete and replaced from source.
- **FR-010**: A completed target MUST be validated on every restart before copy
  is skipped.
- **FR-011**: Any migration or SSO bootstrap failure MUST prevent Jellyfin from
  starting.
- **FR-012**: The Authentik blueprint, encrypted OAuth client secret, client ID,
  redirect URI, scope/claim configuration, group names, and native login behavior
  MUST remain unchanged.
- **FR-013**: Migration and SSO init containers MUST have explicit resource
  requests and limits, and the effective pod scheduling request MUST remain
  bounded by Jellyfin's existing 2 GiB request.
- **FR-014**: Production Flux wiring MUST depend on
  `local-path-provisioner`.
- **FR-015**: A binding ADR MUST record the app-specific exception to the default
  NFS storage decision and the node-affinity/rollback consequences.
- **FR-016**: Evidence MUST distinguish local/unit validation from pending
  development and production authentication acceptance.

## Risk And Validation Expectations

This is a medium-risk Kubernetes storage and app-behavior change. It requires a
focused executable migration test, YAML/render checks, decision metadata checks,
development-cluster validation or an explicit unavailable-infrastructure
exception, and controlled production authentication acceptance. Pod readiness or
the login page alone is insufficient evidence.

## Success Criteria *(mandatory)*

- **SC-001**: Rendered Jellyfin desired state mounts `/config` from
  `jellyfin-config-local-v1` and media from the unchanged NFS export.
- **SC-002**: Migration tests pass for complete copy, idempotent restart, partial
  target replacement, and missing-SSO fail-closed behavior.
- **SC-003**: Neither
  `kubernetes/infra/authentik/blueprints/jellyfin-oauth.yaml` nor
  `kubernetes/apps/jellyfin/secret.yaml` changes in the PR.
- **SC-004**: An existing SSO user, SSO administrator, and native administrator
  all authenticate successfully during controlled cutover acceptance.
- **SC-005**: `jellyfin-config-v2` remains available after cutover.
- **SC-006**: The selected iGPU worker has `MemoryPressure=False` at cutover.

## Assumptions

- The current NFS config PVC contains the complete working Jellyfin and SSO
  state.
- The chart remains pinned to Jellyfin Helm chart `3.2.0`, which supports
  `deploymentStrategy` and ordered `extraInitContainers`.
- `local-path` uses `WaitForFirstConsumer` and `Retain` in production.
- The old pod is fully terminated before the new migration pod starts under
  `Recreate`.
- An operator can perform the live authentication checks before considering the
  rollout accepted.

## Open Questions

- None. The availability tradeoff of node-local config is explicitly accepted
  for this implementation and documented in the binding ADR.
