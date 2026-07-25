---
description: "Implementation tasks for the WireGuard Authentik gate"
---

# Tasks: wireguard-authentik

**Input**: `specs/wireguard-authentik/spec.md` and
`specs/wireguard-authentik/plan.md`
**Risk Tier**: high
**Prerequisites**: Branch `codex/wireguard-authentik` and matching
`specs/wireguard-authentik/` artifacts. The user approved the spec and plan by
requesting implementation.

## Human Gate Status

**Spec Gate**: approved by the user's explicit request to plan the named fix

**Plan Gate**: approved by the user's 2026-07-25 instruction to implement

**Analyze Requirement**: run before source implementation; proceed only with no
critical or high unresolved findings

## Format: `[ID] [P?] [Req] Description`

- **[P]**: Can run in parallel because it touches different files or performs
  read-only validation with no dependency on another incomplete task.
- **[Req]**: Requirement or user-story trace.
- All helper results and command outcomes are consolidated in
  `specs/wireguard-authentik/evidence.md`.

## Phase 1: Setup

**Goal**: Establish approved artifacts and implementation evidence.

- [x] T001 [FR-009] Update human gate status in
      `specs/wireguard-authentik/plan.md` and initialize
      `specs/wireguard-authentik/evidence.md` from the repository template.
- [x] T002 [FR-009] Run Spec Kit analysis across
      `specs/wireguard-authentik/spec.md`,
      `specs/wireguard-authentik/plan.md`, and
      `specs/wireguard-authentik/tasks.md`; resolve no source files until the
      analysis has no critical or high finding.

## Phase 2: User Story 1 - Gate WireGuard Administration (P1)

**Goal**: Every HTTP path on the LAN `vpn` hostname reaches Authentik before
wg-easy and fails closed.

**Independent test**: In a fresh browser context, `/` and `/api/client` on
`https://vpn.lab.petebeegle.com` reach Authentik or an Authentik denial and
expose no wg-easy UI/API response.

- [x] T003 [US1] Add the root and representative API-path Authentik assertions
      to `tests/smoke/routes.spec.js` and mirror them in
      `kubernetes/apps/synthetics/smoke/routes.spec.js`.
- [x] T004 [US1] Run the focused test from `tests/smoke/routes.spec.js` against
      the current production route and record the expected pre-fix failure in
      `specs/wireguard-authentik/evidence.md`.
- [x] T005 [US1] Add the `wireguard-proxy` Proxy Provider, Authentik
      application, and embedded-outpost assignment in
      `kubernetes/infra/authentik/blueprints/wireguard-proxy.yaml`, and register
      the ConfigMap in
      `kubernetes/infra/authentik/blueprints/kustomization.yaml`.
- [x] T006 [US1] Add a least-privilege cross-namespace Service
      `ReferenceGrant` in `kubernetes/infra/authentik/referencegrant.yaml` and
      register it in `kubernetes/infra/authentik/kustomization.yaml`, allowing
      only `wireguard`-namespace HTTPRoutes to reference only
      `authentik-server`.
- [x] T007 [US1] Replace the direct wg-easy backend with
      `authentik/authentik-server:80` in
      `kubernetes/infra/network/vpn/httproute.yaml`, preserving the LAN-only
      Gateway parent and hostname.
- [x] T008 [US1] Add `authentik` to the `vpn` dependency list in
      `kubernetes/clusters/production/infra/vpn.yaml` and add `vpn` to
      `app-synthetics` dependencies in
      `kubernetes/clusters/production/apps/synthetics.yaml`.

## Phase 3: User Story 2 - Preserve Authorized Operations (P2)

**Goal**: Only dedicated WireGuard administrators or built-in Authentik
administrators can pass Authentik, and wg-easy retains its existing inner
authentication.

**Independent test**: An authenticated member of either authorized group reaches
the wg-easy login/UI, while a user in neither group receives an Authentik
authorization denial.

- [x] T009 [US2] Add the `WireGuard Admins` group plus group-policy bindings for
      `WireGuard Admins` or built-in `authentik Admins` break-glass access, with
      no Basic Auth injection or unauthenticated path bypass, in
      `kubernetes/infra/authentik/blueprints/wireguard-proxy.yaml`.
- [x] T010 [US2] Document group membership, double authentication, failure
      behavior, authorized/non-member verification, and Git-revert recovery in
      `docs/runbooks/wireguard.md`.

## Phase 4: User Story 3 - Keep VPN And Automation Stable (P3)

**Goal**: Preserve the WireGuard UDP data plane and trusted direct ClusterIP API
path.

**Independent test**: The rendered UDP and HTTP Services and wg-easy Deployment
remain unchanged, and the evidence handoff includes existing-peer and
credentialed direct-API verification.

- [x] T011 [US3] Review the implementation diff and rendered manifests to prove
      no changes to `kubernetes/infra/network/vpn/service.yaml`,
      `kubernetes/infra/network/vpn/deployment.yaml`, WireGuard persistent
      storage, or `kubernetes/apps/access-broker/configmap.yaml`; record the
      result in `specs/wireguard-authentik/evidence.md`.
- [x] T012 [US3] Add the direct ClusterIP automation boundary and post-rollout
      peer/API verification procedure to `docs/runbooks/wireguard.md`.

## Phase 5: Polish And Cross-Cutting Validation

**Goal**: Keep documentation, generated architecture, validation, and evidence
coherent.

- [x] T013 [P] [FR-008] Add the `vpn` Authentik target and expected behavior to
      `docs/runbooks/synthetic-smoke-tests.md`.
- [x] T014 [FR-007] Regenerate `docs/architecture.md` with
      `python3 tools/architecture/render.py --write`.
- [x] T015 [FR-009] Run smoke mirroring, focused Playwright, Authentik/VPN and
      production renders, generated architecture, diff, secret scan, and full
      pre-commit checks; record exact outcomes in
      `specs/wireguard-authentik/evidence.md`.
- [x] T016 [FR-009] Record `smoke_profile: none` and the development-cluster
      Authentik/VPN omission as the unavailable-infrastructure exception, plus
      the required post-merge Flux, route, persona, peer, direct-API, and
      one-off synthetic verification handoff in
      `specs/wireguard-authentik/evidence.md`.
- [x] T017 [FR-CONVERGE] Run Spec Kit converge against the finished code; if it
      appends tasks to `specs/wireguard-authentik/tasks.md`, complete them and
      rerun convergence.
- [x] T018 [FR-EVIDENCE] Re-check constitution gates, mark all completed tasks,
      and finalize documentation impact, test layers, exceptions, and current
      branch state in `specs/wireguard-authentik/evidence.md`.

## Dependencies

- Phase 1 blocks all source implementation.
- User Story 1 is the MVP and blocks User Story 2 because the group policy binds
  the application created in US1.
- User Story 3 can be reviewed after the route and blueprint edits exist.
- Cross-cutting validation follows all source and documentation edits.
- Convergence follows implementation and may append a final remediation phase.

## Parallel Opportunities

- T013 can run independently after the smoke expectation is stable.
- Read-only review of T011 can run independently of documentation edits.
- Local render commands for Authentik, VPN, and production can run in parallel
  once implementation files are complete.

## Implementation Strategy

1. Establish TDD evidence by adding the exact-path smoke first.
2. Deliver the P1 proxy-mode gate and fail-closed route.
3. Add P2 group authorization without weakening wg-easy's own login.
4. Prove P3 data-plane and machine-client preservation.
5. Complete broad local validation, document the development exception, and
   converge before handoff.
