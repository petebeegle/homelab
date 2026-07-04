# Feature Specification: access-broker-review-admins

**Feature Branch**: `codex/access-broker-review-admins`
**Created**: 2026-07-04
**Status**: Approved for implementation
**Risk Tier**: medium
**Input**: Configure production access-broker so only approved Discord admins can
approve or deny access requests.

## Human Gate Status

**Intent Brief**: Wire the new homelab-access admin allowlist config into the
production access-broker deployment before continuing toward provisioning.

**Clarify Status**: Skipped; the approved admin user ID is known from the
successful Discord smoke request.

**Spec Gate**: Approved by ongoing user instruction to continue implementation.

## Summary

Set `DISCORD_ADMIN_USER_IDS` for access-broker and roll the Pod template so the
new app image and config are loaded.

## Binding Sources

- `AGENTS.md`
- `docs/runbooks/implementation-workflow.md`
- `docs/runbooks/spec-driven-development.md`

## Scope

### In Scope

- Configure Discord user ID `252951660027052033` as an access reviewer admin.
- Force access-broker to repull the mutable `main` image after homelab-access
  PR #7.

### Out Of Scope

- Authentik user creation and WireGuard provisioning.

## Requirements

- **FR-001**: `access-broker-config` MUST set `DISCORD_ADMIN_USER_IDS`.
- **FR-002**: The Deployment Pod template MUST change to roll the workload.
- **FR-003**: The change MUST preserve Gateway API and SOPS invariants.

## Success Criteria

- **SC-001**: Rendered access-broker manifests include the admin user ID and
  rollout annotation.
- **SC-002**: After merge, Flux applies the change and `/access approve` remains
  usable for the configured admin.

## Assumptions

- Discord user ID `252951660027052033` is the intended initial access reviewer.

## Open Questions

- None.
