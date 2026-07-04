# Feature Specification: access-broker-manual-smoke

**Feature Branch**: `codex/access-broker-manual-smoke`
**Created**: 2026-07-04
**Status**: Draft
**Risk Tier**: high
**Input**: User wants to manually smoke test the Discord app in server `#test`.

## Summary

Activate the access broker's current Discord request-intake behavior behind a
public Cloudflare hostname so Discord can validate the Interactions Endpoint URL
and the user can run `/access request` manually.

## Binding Sources

- `AGENTS.md`
- `.specify/memory/constitution.md`
- `docs/runbooks/implementation-workflow.md`
- `docs/runbooks/spec-driven-development.md`
- `docs/decisions/flux-gitops-source-of-truth.md`
- `docs/decisions/cilium-gateway-api-ingress.md`
- `docs/decisions/sops-age-secrets.md`
- `docs/decisions/synology-nfs-storage.md`
- `docs/decisions/tdd-and-development-smoke-evidence.md`

## Scope

### In Scope

- Configure access-broker for `https://onboard.petebeegle.com`.
- Add Discord app ID/public key to the SOPS-encrypted Secret.
- Add Cloudflare Tunnel ingress for `onboard.petebeegle.com`.
- Activate `app-access-broker` in production Flux for manual smoke.

### Out Of Scope

- Discord bot token and outbound Discord API calls.
- Admin approval workflow.
- Authentik account provisioning.
- wg-easy peer creation.
- Channel allowlisting for `#test`.

## User Scenarios & Testing

### User Story 1 - Discord Endpoint Validation (Priority: P1)

As the operator, I can set the Discord Interactions Endpoint URL to the broker
and have Discord validate the endpoint.

**Why this priority**: Discord must validate the endpoint before any slash
command smoke can work through the public webhook path.

**Independent Test**: After Flux applies the PR, set the endpoint to
`https://onboard.petebeegle.com/discord/interactions` in the Discord Developer
Portal and confirm Discord accepts it.

**Acceptance Scenarios**:

1. **Given** the app is deployed and routed publicly, **When** Discord sends a
   signed PING interaction, **Then** the broker validates the signature and
   returns PONG.

### User Story 2 - Manual Request In `#test` (Priority: P2)

As the operator, I can run `/access request` in Discord `#test` and receive an
ephemeral request ID.

**Why this priority**: This proves the request intake path reaches the app and
persists a pending request.

**Independent Test**: Run `/access request` in `#test`.

**Acceptance Scenarios**:

1. **Given** the slash command exists and is run in `#test`, **When** the broker
   receives the signed interaction, **Then** it persists or reuses a pending
   request and replies with an ephemeral request ID.

## Requirements

- **FR-001**: The public endpoint MUST be
  `https://onboard.petebeegle.com/discord/interactions`.
- **FR-002**: Cloudflare Tunnel MUST route `onboard.petebeegle.com` to
  `gateway/public`.
- **FR-003**: The access broker HTTPRoute MUST attach to Gateway
  `gateway/public`, section `http-gateway`.
- **FR-004**: Discord app ID and public key MUST be stored only in SOPS-encrypted
  `secret.yaml`.
- **FR-005**: The broker MUST use `nfs-csi-storage` for request persistence.
- **FR-006**: Evidence MUST distinguish local render checks from manual Discord
  smoke.

## Risk And Validation Expectations

This is high risk because it activates a public routed authentication-adjacent
endpoint. Development cannot fully validate Cloudflare-to-Discord behavior
because the development cluster intentionally omits Cloudflare Tunnel. Required
substitute checks are render, SOPS, route, activation, and generated
architecture checks before manual production smoke.

## Success Criteria

- **SC-001**: `kubectl kustomize kubernetes/apps/access-broker` renders with
  `onboard.petebeegle.com`, encrypted Secret data, `nfs-csi-storage`, and no
  Kubernetes Ingress.
- **SC-002**: `kubectl kustomize kubernetes/apps/cloudflare-tunnels` renders a
  Cloudflare ingress rule for `onboard.petebeegle.com`.
- **SC-003**: Production app activation renders `app-access-broker`.
- **SC-004**: Manual smoke is ready for the Discord Developer Portal endpoint
  URL and `/access request` in `#test`.

## Assumptions

- The user will create or has created DNS/Cloudflare routing for
  `onboard.petebeegle.com` to the existing Cloudflare Tunnel if needed.
- `homelab-access:main` includes the readiness change before this homelab PR is
  merged.

## Open Questions

- None
