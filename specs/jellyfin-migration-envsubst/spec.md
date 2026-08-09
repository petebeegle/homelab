# Feature Specification: jellyfin-migration-envsubst

**Feature Branch**: `codex/jellyfin-migration-envsubst`
**Created**: 2026-08-08
**Status**: Approved
**Risk Tier**: medium
**Input**: User description: "Merged. Verify success, iterate as needed or clean
up migration scripts upon success. Fan out."

## Human Gate Status

**Intent Brief**: Verify the merged Jellyfin config migration end to end, repair
any rollout blocker without weakening storage, GPU, or authentication safety,
and defer cleanup until the migration has actually succeeded.

**Clarify Status**: Skipped. Three independent read-only fanout lanes reproduced
the same exact Flux build failure and identified unescaped shell parameter
expressions as the cause.

**Spec Gate**: Approved by the user's explicit instruction to verify the merge
and iterate as needed.

## Summary

Restore deployment of the already-merged Jellyfin local-config migration. Flux
must be able to process the desired state without changing the migration
script's runtime meaning, after which the migration can run with its existing
authentication, rollback, storage, and GPU safeguards intact.

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

- Make the generated migration script safe for Flux variable substitution.
- Add regression coverage for the exact render-and-substitute path that failed.
- Preserve the runtime shell expressions and migration behavior byte-for-byte
  after Flux substitution.
- Verify the repaired revision through GitHub Actions and layered production
  reconciliation, workload, storage, and user-path evidence.

### Out Of Scope

- Changing Jellyfin storage classes, PVC names, GPU pinning, authentication
  configuration, migration integrity rules, or rollback behavior.
- Applying missing development GPU/VM infrastructure.
- Removing migration assets before the repaired production migration and
  acceptance checks succeed.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Migration Reconciles (Priority: P1)

As the operator, I can merge the repair and have Flux apply the Jellyfin local
config migration rather than rejecting the generated configuration.

**Why this priority**: The original change is fetched but cannot be built, so no
migration behavior can run until substitution succeeds.

**Independent Test**: Render the Jellyfin manifests, run strict Flux
substitution, and confirm the resulting migration script retains every intended
shell expression.

**Acceptance Scenarios**:

1. **Given** the Jellyfin migration script is embedded in a generated
   configuration object, **When** Flux performs strict substitution, **Then** it
   reports no bad-substitution error and preserves the script for runtime.
2. **Given** the repaired revision is merged, **When** production Flux
   reconciles Jellyfin, **Then** the application Kustomization applies that
   revision and starts the migration workload.

### User Story 2 - Safety Is Preserved (Priority: P1)

As a Jellyfin user or administrator, I retain the same storage, authentication,
rollback, and availability safeguards while the rollout blocker is repaired.

**Why this priority**: A syntax workaround is unacceptable if it changes the
migration's fail-closed behavior or identity state.

**Independent Test**: Run the existing migration suite against the substituted
runtime script and compare the rendered workload's claims, init ordering, and
authentication references with the merged design.

**Acceptance Scenarios**:

1. **Given** representative Jellyfin and SSO state, **When** the substituted
   script migrates it, **Then** all existing success, retry, and fail-closed tests
   pass.
2. **Given** the repaired desired state, **When** it renders, **Then** the local
   target, read-only NFS source, `Recreate` strategy, init ordering, and existing
   authentication references remain unchanged.

## Requirements *(mandatory)*

- **FR-001**: A strict local Flux Kustomization build MUST complete without an
  error for the rendered Jellyfin application.
- **FR-002**: Every runtime shell parameter expansion in the migration script
  MUST remain present after Flux substitution.
- **FR-003**: Existing migration tests MUST execute the post-substitution script
  rather than only the repository source.
- **FR-004**: The repair MUST NOT change PVC names, storage classes, deployment
  strategy, init ordering, GPU selection, authentication settings, or rollback
  source retention.
- **FR-005**: Production verification MUST distinguish merged, fetched, applied,
  live workload, storage, and exact user-path layers.
- **FR-006**: Migration cleanup MUST remain deferred until the repaired rollout
  is applied and verified.

## Risk And Validation Expectations

This is a medium-risk Kubernetes and Flux rendering repair. It requires focused
unit tests, exact Kustomize plus strict Flux substitution, Helm/render review,
repository validation, and post-merge production verification. The known
development iGPU fixture limitation remains an explicit exception; substitute
checks must exercise the exact failed rendering path and the production user
path.

## Success Criteria *(mandatory)*

- **SC-001**: A strict local Flux Kustomization build of the rendered Jellyfin
  application exits zero with no `bad substitution` message.
- **SC-002**: All focused migration tests pass using the substituted script.
- **SC-003**: Production Flux applies the repaired merge revision and the live
  Jellyfin deployment uses `Recreate`, the local config PVC, and the expected
  ordered init containers.
- **SC-004**: The exact Jellyfin HTTPS web and SSO-start paths respond without a
  server error after rollout.
- **SC-005**: No migration, storage, or authentication error is present in the
  repaired pod's init status or relevant logs.

## Assumptions

- `kustomize.toolkit.fluxcd.io/substitute: disabled` is the supported Flux
  resource annotation for preserving literal shell expressions in the
  generated migration ConfigMap while leaving substitution enabled elsewhere.
- The old live Jellyfin deployment remains available until the repaired desired
  state builds successfully.
- Cleanup is a separate follow-up implementation after production acceptance.

## Open Questions

- None.
