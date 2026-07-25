# Feature Specification: wireguard-authentik

**Feature Branch**: `codex/wireguard-authentik`
**Created**: 2026-07-25
**Status**: Draft
**Risk Tier**: high
**Input**: User description: "wireguard (vpn.lab.petebeegle.com) isn't behind
authentik. plan a fix and in a separate agent find any other non-authentik apps
(excluding valheim which is a game server)"

## Human Gate Status

**Intent Brief**: Protect the user-facing WireGuard administration UI at
`https://vpn.lab.petebeegle.com` with Authentik, preserve VPN and automation
behavior, exclude Valheim from the related exposure audit, and identify any
other routed apps lacking Authentik. Authentication and a production traffic
path make this high risk. Acceptance requires an unauthenticated browser to
reach Authentik rather than wg-easy, an authorized operator to reach wg-easy,
an unauthorized authenticated user to be denied, and existing WireGuard peers
and in-cluster automation to remain functional.

**Clarify Status**: skipped; repository conventions and the administrative
nature of wg-easy support the conservative default of a dedicated authorized
operator group while preserving wg-easy's own credential as defense in depth.

**Spec Gate**: approved by the user's explicit request to plan this specific
fix, with assumptions called out below; implementation remains gated on plan
approval.

## Summary

The WireGuard administration hostname must require Authentik authentication and
authorization before a user can reach wg-easy. The protection must apply to the
browser-facing Gateway route without interrupting the WireGuard UDP service,
existing client tunnels, or trusted in-cluster automation that talks directly
to the wg-easy Service. Operators also need automated evidence that the
unauthenticated URL can no longer expose the wg-easy login or administration
shell.

## Binding Sources

- `AGENTS.md`
- `.specify/memory/constitution.md`
- `docs/decisions/cilium-gateway-api-ingress.md`
- `docs/decisions/tdd-and-development-smoke-evidence.md`
- `docs/runbooks/implementation-workflow.md`
- `docs/runbooks/development-cluster.md`
- `docs/runbooks/wireguard.md`
- `docs/runbooks/synthetic-smoke-tests.md`

## Scope

### In Scope

- Put `https://vpn.${cluster_domain}` behind an Authentik application and proxy
  provider on the existing LAN HTTPS Gateway path.
- Limit access to a dedicated WireGuard administrator group while preserving
  built-in Authentik administrators for break-glass access.
- Preserve wg-easy's internal authentication and direct cluster Service for
  trusted automation as defense in depth.
- Add user-path smoke coverage for the unauthenticated Authentik redirect/login
  behavior.
- Update the WireGuard runbook with the authentication path, authorization
  model, validation, and recovery checks.
- Record the separately requested read-only audit of other non-Authentik routed
  apps, excluding Valheim, as planning input only.

### Out Of Scope

- Exposing the wg-easy administration UI on the WireGuard external Gateway or
  the internet-public Gateway.
- Changing WireGuard UDP transport, peer configuration, DNS, AllowedIPs, or
  persistent database contents.
- Replacing the access-broker's direct in-cluster wg-easy API integration.
- Removing wg-easy's own credential or changing its local user database.
- Remediating the other applications found by the exposure audit; each
  materially different app should receive its own implementation decision.
- Adding Authentik to Valheim or treating protocol-only game traffic as a web
  authentication target.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Gate WireGuard Administration (Priority: P1)

An unauthenticated person who opens the WireGuard administration URL must be
sent to Authentik and must not see wg-easy content or APIs.

**Why this priority**: The current direct route exposes a security-sensitive
administration surface before the central identity and policy layer.

**Independent Test**: Open the exact URL in a fresh browser context with no
cookies and assert that the resulting page or redirect belongs to Authentik,
with no wg-easy administration shell or API response exposed.

**Acceptance Scenarios**:

1. **Given** a browser has no Authentik session, **When** it requests
   `https://vpn.lab.petebeegle.com/`, **Then** it reaches the Authentik login
   flow before any wg-easy UI content.
2. **Given** a browser has no Authentik session, **When** it requests a wg-easy
   API path through the `vpn` hostname, **Then** it cannot receive the upstream
   wg-easy API response without first passing Authentik.
3. **Given** Authentik is unavailable, **When** a new unauthenticated request
   reaches the `vpn` hostname, **Then** access fails closed rather than routing
   directly to wg-easy.

### User Story 2 - Preserve Authorized Operations (Priority: P2)

An authorized WireGuard operator can complete Authentik login and reach the
existing wg-easy UI, while other authenticated users remain denied.

**Why this priority**: Authentication alone is insufficient for an
administrative surface; explicit authorization limits the blast radius of a
normal homelab account.

**Independent Test**: Verify one account in the WireGuard administrator group
can reach the wg-easy login/UI after Authentik, and one authenticated account
outside the group receives an authorization denial.

**Acceptance Scenarios**:

1. **Given** an authenticated user belongs to the WireGuard administrator
   group, **When** the user opens the `vpn` hostname, **Then** Authentik permits
   the request and the existing wg-easy authentication/UI remains usable.
2. **Given** an authenticated user does not belong to the WireGuard
   administrator group, **When** the user opens the `vpn` hostname, **Then**
   Authentik denies access without forwarding the request to wg-easy.

### User Story 3 - Keep VPN And Automation Stable (Priority: P3)

Existing WireGuard clients and trusted in-cluster automation continue to work
without traversing browser SSO.

**Why this priority**: The UI security fix must not interrupt the UDP data plane
or access-broker peer provisioning.

**Independent Test**: Confirm the UDP Service and wg-easy workload are unchanged,
an existing peer can still use the VPN service plane, and an in-cluster
credentialed API probe to `wireguard-http.wireguard.svc.cluster.local:51821`
still receives the expected authenticated behavior.

**Acceptance Scenarios**:

1. **Given** an existing WireGuard peer, **When** the route protection is
   reconciled, **Then** the peer can still establish a tunnel and reach its
   existing allowed service-plane destinations.
2. **Given** trusted in-cluster automation uses the ClusterIP Service with the
   existing wg-easy credential, **When** it performs its supported operation,
   **Then** the request bypasses the browser Gateway only and continues to work.

## Requirements *(mandatory)*

- **FR-001**: The implementation MUST require Authentik authentication for
  every HTTP path served through `https://vpn.${cluster_domain}`.
- **FR-002**: The implementation MUST restrict the Authentik application to a
  dedicated WireGuard administrator group, with the built-in Authentik
  administrator group retained as a break-glass path.
- **FR-003**: The `vpn` hostname MUST fail closed when Authentik or its proxy
  component cannot authorize a request.
- **FR-004**: The browser-facing HTTPRoute MUST continue to use Cilium Gateway
  API and MUST NOT add a traditional Kubernetes Ingress.
- **FR-005**: The implementation MUST preserve the WireGuard UDP Service,
  existing peer configuration, wg-easy persistent data, and direct in-cluster
  Service access.
- **FR-006**: The implementation MUST preserve wg-easy's own authentication as
  defense in depth and for existing API clients.
- **FR-007**: The Authentik configuration and Gateway backend references MUST
  be fully expressed in Git and reconciled by Flux.
- **FR-008**: The implementation MUST add an automated unauthenticated smoke
  assertion for the exact `vpn` hostname and keep mirrored synthetic smoke
  sources synchronized.
- **FR-009**: Evidence MUST distinguish local render checks, development
  validation or its production-only exception, production synthetic smoke,
  authorized/unauthorized account checks, UDP peer verification, and direct
  automation verification.
- **FR-010**: Documentation MUST describe normal access, group membership,
  failure behavior, verification, and rollback without revealing credentials.

## Risk And Validation Expectations

This is a high-risk authentication and production traffic-path change. Use
focused manifest tests, broad Kubernetes/Flux render checks, an independent
read-only review lane, and development-cluster validation where the environment
can represent the changed resources. Because the standard development base
omits both Authentik and VPN, any untestable production-only layer requires an
explicit exception plus substitute local, synthetic, and live read-only checks.
Successful completion requires the exact user path; readiness and
`Accepted=True` alone are insufficient.

## Success Criteria *(mandatory)*

- **SC-001**: 100% of unauthenticated requests tested at the `vpn` hostname,
  including `/` and a representative API path, reach Authentik or an
  Authentik-generated denial and expose no wg-easy response.
- **SC-002**: A WireGuard administrator or built-in Authentik administrator
  reaches the existing wg-easy UI, while an authenticated user in neither group
  is denied in the same release verification.
- **SC-003**: At least one existing WireGuard peer and the credentialed
  in-cluster wg-easy API path pass post-change verification with no peer
  recreation or credential migration.
- **SC-004**: Local policy/render checks and the production synthetic smoke
  complete successfully, with every unavailable development layer explicitly
  recorded.
- **SC-005**: The `vpn` route has accepted and resolved backend references and
  the exact browser URL demonstrates the intended Authentik behavior after Flux
  applies the target revision.

## Assumptions

- The desired audience is `WireGuard Admins`, with the existing `authentik
  Admins` group as a break-glass path rather than all Authentik users, because
  wg-easy can create, revoke, and reveal VPN client configurations.
- Authentik proxy mode is preferred over native wg-easy OIDC because the pinned
  wg-easy v15 documentation exposes local initial credentials but no supported
  native OIDC configuration.
- The existing LAN-only `gateway/internal` exposure remains intentional; this
  change does not add `gateway/external` or `gateway/public`.
- The access-broker continues to use the direct ClusterIP Service and existing
  wg-easy credentials, so browser SSO does not become a machine-to-machine
  dependency.
- The separately requested audit informs follow-up prioritization but does not
  expand this implementation into a multi-app authentication migration.

## Open Questions

- None. Populate `WireGuard Admins` through an existing `authentik Admins`
  account after the blueprint reconciles.
