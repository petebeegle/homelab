# Feature Specification: wireguard-authentik-outpost

**Feature Branch**: `codex/wireguard-authentik-outpost`
**Created**: 2026-07-25
**Status**: Approved for implementation
**Risk Tier**: high
**Input**: Correct the merged WireGuard Authentik proxy so successful
authentication reaches the wg-easy UI instead of leaving users at Authentik.

## Human Gate Status

**Intent Brief**: The user reported that `https://vpn.lab.petebeegle.com/`
terminates at Authentik instead of authenticating and proxying to WireGuard.

**Clarify Status**: No critical ambiguity. The expected behavior is explicit:
unauthenticated requests enter Authentik, authorized sessions reach wg-easy,
and direct unauthenticated access remains blocked.

**Spec Gate**: Approved by the user's correction of the deployed behavior.

## User Scenarios

### User Story 1 - Authorized administrator reaches wg-easy (P1)

After authenticating with an allowed Authentik identity, a WireGuard
administrator reaches the wg-easy application at the original VPN URL.

**Independent Test**: Confirm an authenticated request is handled by the
WireGuard proxy provider and returns wg-easy rather than Authentik's application
UI or a 404.

### User Story 2 - Unauthenticated access remains denied (P1)

An unauthenticated request to either the UI or its API cannot reach wg-easy
without completing Authentik authentication and authorization.

**Independent Test**: Request `/` and `/api/client` without a session and
confirm the response is an Authentik authorization path, never a wg-easy
response.

## Requirements

- **FR-001**: The WireGuard proxy provider MUST be assigned to the active
  embedded Authentik outpost after every blueprint reconciliation.
- **FR-002**: The authoritative outpost provider list MUST preserve every
  existing proxy provider while adding WireGuard.
- **FR-003**: Authenticated, authorized traffic MUST proxy to the existing
  wg-easy Service.
- **FR-004**: Unauthenticated UI and API traffic MUST remain unable to reach
  wg-easy.
- **FR-005**: Durable state MUST be GitOps-managed and any affected secret
  manifest MUST remain SOPS-encrypted.
- **FR-006**: Automated smoke assertions MUST recognize the current Authentik
  flow and distinguish Authentik handling from successful wg-easy proxying.
- **FR-007**: Operators MUST have a runbook for adding an Authentik proxy
  application without creating competing ownership of the embedded-outpost
  provider list.
- **FR-008**: The runbook MUST cover blueprint design, safe SOPS editing,
  required render and smoke validation, post-merge reconciliation checks, and
  rollback/troubleshooting for provider-list races.
- **FR-009**: Exactly one Flux Kustomization MUST own the
  `private-authentik-blueprints` Secret, and that Secret MUST retain both the
  proxy and icon blueprint keys.

## Success Criteria

- **SC-001**: Live embedded-outpost state contains WireGuard and all previously
  assigned proxy providers.
- **SC-002**: Live proxy logs identify the WireGuard provider when serving the
  VPN hostname.
- **SC-003**: An authorized browser reaches wg-easy at the VPN URL.
- **SC-004**: Unauthenticated checks for `/` and `/api/client` do not expose
  wg-easy.
- **SC-005**: An operator can follow one documented procedure to add a proxy
  while preserving all existing embedded-outpost assignments.

## Edge Cases

- A later blueprint reconciliation must not remove WireGuard from the outpost.
- Existing proxy applications must not lose their outpost assignments.
- A fresh Authentik worker start must converge to the same provider list.
- Reconciliation of an application Kustomization must not remove another
  Authentik blueprint key from the mounted Secret.

## Out of Scope

- Replacing wg-easy's application or changing WireGuard tunnel traffic.
- Reworking unrelated Authentik proxy applications.

## Assumptions

- The existing private proxy blueprint is the authoritative owner of the
  embedded outpost's complete provider list.
- Existing administrators remain the break-glass authorization path.

## Binding Sources

- `AGENTS.md`
- `.specify/memory/constitution.md`
- `docs/decisions/flux-gitops-source-of-truth.md`
- `docs/runbooks/spec-driven-development.md`
- `docs/runbooks/implementation-workflow.md`
