# Feature Specification: 1Password Rate-Limit Fix

**Feature Branch**: `codex/onepassword-rate-limit-fix`
**Created**: 2026-08-11
**Status**: Approved for incident correction
**Risk Tier**: high
**Input**: User request: "there are alerts around 1pass. fix"

## Human Gate Status

**Intent Brief**: Restore reliable 1Password synchronization without silencing valid alerts, exposing credentials, deploying Connect, or changing consumers.

**Clarify Status**: Skipped. Live metadata and service-account quota state identified an unambiguous failure and sustainable bound.

**Spec Gate**: Approved by the user's direct request to diagnose and fix the active alert condition.

## Summary

Keep both direct-auth operators within the account-wide daily read quota so synchronized items remain Ready and alerts represent actionable failures.

## Binding Sources

- `AGENTS.md`
- `.specify/memory/constitution.md`
- `docs/runbooks/implementation-workflow.md`
- `docs/runbooks/onepassword-operator.md`
- `docs/decisions/flux-gitops-source-of-truth.md`
- `docs/decisions/tdd-and-development-smoke-evidence.md`

## Scope

### In Scope

- Set production to a quota-safe polling interval and make development effectively manual-refresh only.
- Add a policy regression check for the interval.
- Document rate-limit diagnosis and expected rotation latency.
- Validate the shared development base before production-oriented completion.

### Out Of Scope

- Deploying 1Password Connect or migrating to 1Password Environments.
- Increasing the external 1Password subscription quota.
- Cutting workloads over from SOPS or weakening the alerts.

## User Scenarios & Testing

### User Story 1 - Sustainable synchronization (Priority: P1)

As the cluster operator, I need direct-auth polling to stay within the shared account quota so all published items can refresh continuously.

**Independent Test**: Render production with a 3600-second interval and development with a one-year interval, then reconcile the exact branch through the development base.

**Acceptance Scenarios**:

1. **Given** production with 17 items, **when** it polls hourly and development uses effective manual-only refresh, **then** baseline reads are approximately 408/day and stay below the observed 1000/day account limit.
2. **Given** the quota is exhausted, **when** the change reconciles, **then** existing generated Secrets remain present and synchronization can recover after provider reset.
3. **Given** development does not require automatic refresh, **when** an operator annotates a development `OnePasswordItem`, **then** its controller event explicitly reconciles that item.

### User Story 2 - Actionable diagnosis (Priority: P2)

As the cluster operator, I need to distinguish quota exhaustion from missing items or bad credentials without displaying values.

**Independent Test**: Review the runbook commands and policy tests.

**Acceptance Scenarios**:

1. **Given** all items become unready together, **when** the runbook is used, **then** quota metadata and the reset window can be inspected without printing the token.

## Requirements

- **FR-001**: Production MUST set `operator.pollingInterval` to `3600` seconds.
- **FR-002**: Development MUST set `operator.pollingInterval` to `31536000` seconds because operator 1.12.0 cannot disable its ticker with zero; item annotation updates MUST be documented as the explicit refresh trigger.
- **FR-003**: Connect MUST remain disabled and direct service-account authentication enabled.
- **FR-004**: Existing alert thresholds and generated Secrets MUST be preserved.
- **FR-005**: The runbook MUST explain quota inspection, account-wide budgeting, and up-to-one-hour automatic rotation latency.
- **FR-006**: Evidence MUST record the live failure, quota metadata, render and policy checks, and development validation.

## Success Criteria

- **SC-001**: Cluster-specific rendering shows production `POLLING_INTERVAL=3600` and development `POLLING_INTERVAL=31536000`, with no Connect workload or token-valued Secret.
- **SC-002**: Policy tests pass and prove `300` is rejected.
- **SC-003**: Exact-branch development reconciliation leaves the operator available with the intended interval.
- **SC-004**: No Secret value or 1Password token appears in Git, logs, or evidence.

## Assumptions

- The observed account-wide read limit is 1000/day.
- Each item causes approximately one baseline read per polling cycle; hourly production polling for 17 items uses about 408 reads/day, while development periodic reads are negligible.
- Provider quota reset is required before currently unready production items can recover.

## Open Questions

- None.
