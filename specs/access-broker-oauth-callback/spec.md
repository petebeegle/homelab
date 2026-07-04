# Feature Specification: access-broker-oauth-callback

**Feature Branch**: `codex/access-broker-oauth-callback`
**Created**: 2026-07-04
**Status**: Approved for implementation
**Risk Tier**: medium
**Input**: User needs the deployed access broker to support Discord's OAuth
code-grant redirect during manual smoke testing.

## Human Gate Status

**Intent Brief**: Complete the Discord install path for the production
`onboard.petebeegle.com` access broker so a redirect to `/oauth/callback` does
not 404 and the updated application image rolls through GitOps.

**Clarify Status**: Skipped. The user provided direct implementation approval
after the 404 and Discord `Missing Access` failure made the required route
clear.

**Spec Gate**: Approved by direct user instruction: "you fucking do it."

## Summary

The production access-broker deployment should explicitly configure the Discord
OAuth redirect URI and roll the Pod template so the merged `homelab-access`
callback implementation is pulled and served.

## Binding Sources

- `AGENTS.md`
- `.specify/memory/constitution.md`
- `docs/runbooks/implementation-workflow.md`
- `docs/runbooks/spec-driven-development.md`

## Scope

### In Scope

- Configure `DISCORD_REDIRECT_URI=https://onboard.petebeegle.com/oauth/callback`.
- Force a durable Deployment rollout through a GitOps-owned Pod template change.
- Record validation and the remaining client-secret requirement.

### Out Of Scope

- Committing plaintext Discord client secrets.
- Completing Authentik or WireGuard provisioning.

## User Scenarios & Testing

### User Story 1 - Callback Route Is Served (Priority: P1)

The operator installs the Discord app with a code-grant redirect and lands on
the access broker instead of a generic 404.

**Why this priority**: This unblocks the manual Discord smoke path.

**Independent Test**: Render the access-broker manifests and verify the
redirect URI and rollout annotation are present.

**Acceptance Scenarios**:

1. **Given** the access broker is deployed from GitOps, **When** Discord
   redirects to `/oauth/callback`, **Then** the request reaches the access
   broker callback handler.

## Requirements

- **FR-001**: The access-broker ConfigMap MUST set
  `DISCORD_REDIRECT_URI=https://onboard.petebeegle.com/oauth/callback`.
- **FR-002**: The Deployment Pod template MUST change so Flux rolls a fresh Pod
  that pulls `ghcr.io/petebeegle/homelab-access:main`.
- **FR-003**: The implementation MUST preserve Gateway API usage and avoid
  Kubernetes `Ingress`.
- **FR-004**: Evidence MUST record that Discord `DISCORD_CLIENT_SECRET` is still
  required to complete the code exchange.

## Risk And Validation Expectations

Medium Kubernetes application configuration change. Run focused kustomize render
checks and production post-merge verification; development validation is
unavailable for this Discord production app/install path and must be recorded as
an exception.

## Success Criteria

- **SC-001**: `kubectl kustomize kubernetes/apps/access-broker` renders the
  redirect URI and rollout annotation.
- **SC-002**: After merge and Flux apply, the live Deployment includes the new
  config and `/oauth/callback` no longer returns the generic route 404.

## Assumptions

- `homelab-access` PR #5 is merged before this GitOps change is deployed.
- The Discord Client Secret cannot be derived from the bot token or public key
  and must come from the Developer Portal.

## Open Questions

- None for this PR. The operator still needs to provide `DISCORD_CLIENT_SECRET`
  for a successful OAuth exchange.
