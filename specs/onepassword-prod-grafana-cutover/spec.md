# Feature Specification: Production Grafana Credential Cutover

**Feature Branch**: `codex/onepassword-prod-grafana-cutover`
**Created**: 2026-08-29
**Status**: Spec approved; planning
**Risk Tier**: high
**Input**: User description: "Cut over one production consumer that can be manually smoke tested without bringing everything down."

## Human Gate Status

**Intent Brief**: Move one isolated production consumer from its legacy SOPS credential to its already-published 1Password copy. Minimize blast radius, preserve immediate rollback, and provide a manual user-path smoke test before the change is accepted.

**Clarify Status**: Skipped because the low-blast-radius requirement selects Grafana cleanly and the existing migration plan already separates Grafana credentials from monitoring notification delivery.

**Spec Gate**: Approved by the user with “get going” after review of the Grafana-only scope.

## Summary

Move Grafana's administrator and OAuth credential consumption to the existing 1Password-generated credential while retaining the legacy credential for rapid rollback. The change must affect only Grafana authentication and credential-dependent operator access. Grafana notification delivery and all other production consumers remain unchanged.

## Binding Sources

- `AGENTS.md`
- `.specify/memory/constitution.md`
- `docs/decisions/flux-gitops-source-of-truth.md`
- `docs/decisions/sops-age-secrets.md`
- `docs/decisions/tdd-and-development-smoke-evidence.md`
- `docs/runbooks/implementation-workflow.md`
- `docs/runbooks/development-cluster.md`
- `docs/runbooks/onepassword-operator.md`

## Scope

### In Scope

- Switch every Grafana consumer of the `grafana-credentials` credential family to the existing 1Password-generated copy.
- Preserve the legacy `grafana-credentials` copy and its decryption path as an individual rollback target.
- Verify that the generated credential is ready and byte-identical to the legacy credential without displaying values.
- Verify Grafana rollout, availability, authentication, dashboards, data sources, and credential-dependent operator reconciliation.
- Provide a concise manual smoke sequence at `https://monitoring.lab.petebeegle.com` and stop before acceptance if it fails.

### Out Of Scope

- The separate `grafana-env` Discord webhook credential and notification-delivery cutover.
- Changes to Grafana users, passwords, OAuth client registration, dashboards, alerts, data sources, routes, or storage.
- Authentik, cert-manager, private Flux Git access, WireGuard, or any application credential cutover.
- Removal of SOPS manifests, Flux decryption, Age bootstrap, or rollback credentials.
- Rotation of any credential value.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Use Grafana After Isolated Credential Cutover (Priority: P1)

As the homelab operator, I can open Grafana, authenticate through the existing login path, and use dashboards after Grafana switches to its 1Password-generated credential.

**Why this priority**: It proves the smallest production cutover that a human can validate without risking unrelated services.

**Independent Test**: Open the production Grafana URL, complete the existing login flow, load a known dashboard, and confirm panels return data.

**Acceptance Scenarios**:

1. **Given** the generated Grafana credential is ready and matches the legacy credential, **when** Grafana is cut over and reconciled, **then** Grafana remains available and its workload becomes ready without affecting unrelated workloads.
2. **Given** the cutover has reconciled, **when** the operator signs in through the existing authentication flow, **then** authentication succeeds and a known dashboard displays live data.
3. **Given** Grafana is using the generated credential, **when** credential-dependent dashboard management reconciles, **then** it remains healthy and dashboards continue to be managed.

### User Story 2 - Roll Back Only Grafana (Priority: P2)

As the homelab operator, I can restore Grafana's legacy credential references without changing any other migration consumer if acceptance fails.

**Why this priority**: A narrow and rehearsable rollback is the main safety property of this first production consumer cutover.

**Independent Test**: Review the desired-state diff and confirm every changed reference can be reverted from the generated credential name to the retained legacy name in one Grafana-only revert.

**Acceptance Scenarios**:

1. **Given** any Grafana smoke check fails, **when** the Grafana-only change is reverted, **then** all Grafana consumers return to the retained legacy credential without modifying 1Password items or other workloads.
2. **Given** Grafana acceptance passes, **when** the implementation is complete, **then** the legacy credential remains present for later retirement rather than being deleted.

## Requirements *(mandatory)*

- **FR-001**: Every Grafana consumer of administrator or OAuth credentials MUST reference the existing 1Password-generated Grafana credential after cutover.
- **FR-002**: The separate notification webhook credential MUST continue using its current legacy source.
- **FR-003**: The legacy Grafana credential and its decryption support MUST remain available for rollback.
- **FR-004**: Generated and legacy Grafana credentials MUST have identical key sets and bytes before any consumer change is accepted, and validation MUST not print values.
- **FR-005**: The generated credential MUST report ready before cutover.
- **FR-006**: Grafana availability, workload readiness, authentication, a known dashboard, live panel data, data-source health, and credential-dependent dashboard management MUST be verified after reconciliation.
- **FR-007**: The implementation MUST leave Authentik, certificate issuance, private Git reconciliation, WireGuard, alert delivery, and application consumers unchanged.
- **FR-008**: A failed acceptance check MUST result in a Grafana-only reference rollback; the generated credential resource MUST NOT be deleted as a rollback mechanism.
- **FR-009**: Evidence MUST record the pushed revision, fetched and applied revisions, live reference names, readiness, automated checks, manual smoke result, rollback state, and cleanup without credential values.

## Risk And Validation Expectations

This is high risk because it changes production authentication credentials. Validation requires strict rendering and policy checks, no-output parity, current production readiness, a controlled Grafana rollout, automated health and API checks, and the exact manual login/dashboard path. Development does not run the monitoring stack, so evidence must record that infrastructure gap and use local rendering plus the isolated production rollout with a retained one-change rollback.

## Success Criteria *(mandatory)*

- **SC-001**: Exactly one production credential family changes consumers, and all unrelated production secret references remain unchanged.
- **SC-002**: No-output comparison reports full key and byte parity before cutover.
- **SC-003**: Grafana returns to one ready replica within ten minutes of reconciliation and remains reachable at its existing URL.
- **SC-004**: The operator completes login and loads one known dashboard with live data within five minutes.
- **SC-005**: All credential-dependent dashboard-management resources remain healthy after cutover.
- **SC-006**: The legacy credential remains present and a Grafana-only revert is available throughout acceptance.

## Assumptions

- `grafana-credentials-onepassword` remains read-only, ready, and byte-identical to `grafana-credentials`.
- Existing administrator and Authentik OAuth behavior is correct before cutover; this change does not rotate or repair credentials.
- Grafana is sufficiently isolated that a failed rollout does not interrupt metrics collection, logging, certificates, networking, GitOps reconciliation, or application traffic.
- Manual smoke will be performed by the user after the PR merges and before the cutover is declared accepted.

## Open Questions

- None.
