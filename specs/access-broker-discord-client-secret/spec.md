# Feature Specification: access-broker-discord-client-secret

**Feature Branch**: `codex/access-broker-discord-client-secret`
**Created**: 2026-07-04
**Status**: Approved for implementation
**Risk Tier**: medium
**Input**: Add the Discord Client Secret to access-broker so manual OAuth smoke
can complete.

## Human Gate Status

**Intent Brief**: Store the Discord Client Secret in the SOPS-encrypted
access-broker Secret and deploy it through GitOps.

**Clarify Status**: Skipped; the user provided the exact secret value and prior
smoke proved this is the remaining blocker.

**Spec Gate**: Approved by direct user instruction.

## Summary

Add `DISCORD_CLIENT_SECRET` to the access-broker SOPS Secret without committing
plaintext secret material.

## Binding Sources

- `AGENTS.md`
- `docs/runbooks/implementation-workflow.md`
- `docs/runbooks/spec-driven-development.md`

## Scope

### In Scope

- Add encrypted `DISCORD_CLIENT_SECRET` to
  `kubernetes/apps/access-broker/secret.yaml`.
- Validate the manifest remains SOPS-encrypted.
- Deploy via PR and Flux, then smoke the Discord callback path.

### Out Of Scope

- Changing app code, routes, Authentik provisioning, or WireGuard provisioning.

## User Scenarios & Testing

### User Story 1 - OAuth Code Exchange Can Run (Priority: P1)

**Independent Test**: After Flux applies the secret, a Discord install redirect
can reach `/oauth/callback` with `DISCORD_CLIENT_SECRET` present.

**Acceptance Scenarios**:

1. **Given** Discord redirects with an authorization code, **When** the callback
   handler runs, **Then** it can authenticate to Discord's token endpoint using
   the configured client secret.

## Requirements

- **FR-001**: `access-broker-secret` MUST include encrypted
  `DISCORD_CLIENT_SECRET`.
- **FR-002**: The secret value MUST NOT appear in plaintext in committed files.
- **FR-003**: Evidence MUST record SOPS and render validation.

## Success Criteria

- **SC-001**: `sops filestatus kubernetes/apps/access-broker/secret.yaml`
  reports encrypted.
- **SC-002**: Secret manifest contains the `DISCORD_CLIENT_SECRET` key only as
  encrypted SOPS data.

## Assumptions

- PR #354 has routed `/oauth/callback` to access-broker.

## Open Questions

- None.
