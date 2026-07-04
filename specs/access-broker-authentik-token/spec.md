# Feature Specification: access-broker-authentik-token

**Feature Branch**: `codex/access-broker-authentik-token`
**Created**: 2026-07-04
**Status**: Approved for implementation
**Risk Tier**: medium
**Input**: Wire access-broker with Authentik API credentials after
homelab-access gained Authentik user provisioning on approval.

## Human Gate Status

**Intent Brief**: Let production access-broker call Authentik when an admin
approves a Discord access request.

**Clarify Status**: Skipped; the app behavior is merged and the missing runtime
secret is known.

**Spec Gate**: Approved by ongoing user instruction to continue implementation.

## Summary

Add `AUTHENTIK_TOKEN` to the SOPS-encrypted access-broker Secret by copying the
existing Authentik bootstrap token, then roll access-broker so the new app image
and token are loaded.

## Binding Sources

- `AGENTS.md`
- `docs/runbooks/implementation-workflow.md`
- `docs/runbooks/spec-driven-development.md`

## Scope

### In Scope

- Add encrypted `AUTHENTIK_TOKEN` to `access-broker-secret`.
- Update access-broker rollout annotation.
- Validate SOPS encryption and render output.

### Out Of Scope

- WireGuard peer/config provisioning.

## Requirements

- **FR-001**: `access-broker-secret` MUST include encrypted `AUTHENTIK_TOKEN`.
- **FR-002**: The plaintext token MUST NOT be committed.
- **FR-003**: The Deployment Pod template MUST change to roll the workload.

## Success Criteria

- **SC-001**: SOPS file status reports encrypted.
- **SC-002**: Rendered access-broker manifests include encrypted
  `AUTHENTIK_TOKEN` and the rollout annotation.

## Assumptions

- The existing Authentik bootstrap token is acceptable for this smoke-stage
  provisioning integration.

## Open Questions

- None.
