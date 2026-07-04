# Feature Specification: access-broker-oauth-route

**Feature Branch**: `codex/access-broker-oauth-route`
**Created**: 2026-07-04
**Status**: Approved for implementation
**Risk Tier**: medium
**Input**: Public smoke showed `/oauth/callback` still returns Cloudflare 404
because the access-broker HTTPRoute does not match that path.

## Human Gate Status

**Intent Brief**: Route Discord OAuth callback traffic for
`onboard.petebeegle.com` to access-broker.

**Clarify Status**: Skipped; live route inspection identified the missing match.

**Spec Gate**: Approved by ongoing user instruction to do the implementation.

## Summary

Add `/oauth/callback` to the public access-broker HTTPRoute so Discord install
redirects reach the broker callback handler.

## Binding Sources

- `AGENTS.md`
- `docs/runbooks/implementation-workflow.md`
- `docs/runbooks/spec-driven-development.md`

## Scope

### In Scope

- Add an exact `/oauth/callback` HTTPRoute match.
- Validate render, no Ingress, Flux apply, and public callback behavior.

### Out Of Scope

- Adding `DISCORD_CLIENT_SECRET`; the real secret is still required separately.

## User Scenarios & Testing

### User Story 1 - OAuth Callback Reaches Broker (Priority: P1)

**Independent Test**: Public curl to
`https://onboard.petebeegle.com/oauth/callback?code=fake-code` returns the
broker's configured-secret error rather than Cloudflare 404.

**Acceptance Scenarios**:

1. **Given** Discord redirects to `/oauth/callback`, **When** the request enters
   Cloudflare Tunnel and Gateway, **Then** Cilium routes it to access-broker.

## Requirements

- **FR-001**: `access-broker-public` MUST route exact path `/oauth/callback`.
- **FR-002**: The change MUST preserve Gateway API and avoid Kubernetes
  `Ingress`.
- **FR-003**: Evidence MUST record public URL behavior after merge.

## Success Criteria

- **SC-001**: Access-broker package render includes `/oauth/callback`.
- **SC-002**: Public callback URL no longer returns Cloudflare 404.

## Assumptions

- PR #353 has already deployed the callback-capable application code.

## Open Questions

- None.
