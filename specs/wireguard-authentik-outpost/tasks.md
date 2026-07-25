# Tasks: wireguard-authentik-outpost

**Input**: `spec.md` and `plan.md`
**Risk Tier**: high

## Phase 1: Regression Evidence

- [x] T001 [US1] Record live proof that WireGuard exists as a proxy provider but
      is absent from the embedded outpost in `evidence.md`.
- [x] T002 [US1] Record blueprint apply ordering that demonstrates the
      competing provider-list ownership in `evidence.md`.
- [x] T003 [US2] Correct the focused unauthenticated smoke contract in
      `tests/smoke/routes.spec.js` and its deployed mirror.

## Phase 2: Implementation

- [x] T004 [US1] Remove embedded-outpost ownership from
      `kubernetes/infra/authentik/blueprints/wireguard-proxy.yaml`.
- [x] T005 [US1] Add the WireGuard provider to the complete outpost provider
      list inside SOPS-encrypted `kubernetes/infra/authentik/secret.yaml`.
- [x] T006 [US1] Verify all six existing provider assignments remain present
      alongside WireGuard and consolidate both private blueprint keys under one
      encrypted Secret owner without emitting secret plaintext.

## Phase 3: Verification

- [x] T007 [US1] Validate Authentik blueprint structure and rendered manifests.
- [x] T008 [US2] Validate SOPS encryption and scan for plaintext leakage.
- [x] T009 [US2] Run local synthetic smoke lint/list checks and mirror checks.
- [x] T010 Record development-cluster exception and substitute evidence in
      `evidence.md`.
- [x] T011 [US1] Add the proxy onboarding, SOPS, validation, troubleshooting,
      and rollback procedure to `docs/runbooks/authentik-proxy-apps.md`.
- [x] T012 Run convergence analysis and close any remaining requirements.

## Phase 4: Delivery

- [ ] T013 Commit, push, open a PR, and merge after required checks.
- [ ] T014 Verify Flux reconciliation, live outpost membership, unauthenticated
      denial, and authenticated wg-easy landing after merge.
