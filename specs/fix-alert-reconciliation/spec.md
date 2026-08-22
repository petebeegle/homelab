# Feature Specification: Fix Alert Reconciliation

**Feature Branch**: `codex/fix-alert-reconciliation`
**Created**: 2026-08-22
**Status**: Approved for incident correction
**Risk Tier**: high

## Human Gate Status

**Intent Brief**: Stop recurring Grafana alerts caused by failed Flux reconciliation without silencing real alerts or changing credentials.

**Clarify Status**: Skipped; live Flux status identifies the exact missing substitution value.

**Spec Gate**: Approved by the user's direct request to resolve continuing alerts.

## Summary

Prevent Flux from interpreting the Grafana dashboard's runtime datasource placeholder as a cluster substitution. The existing Grafana datasource reference must reach Grafana unchanged.

## Scope

### In Scope

- Escape the Grafana dashboard runtime datasource placeholder from Flux substitution.
- Verify the rendered dashboard retains the runtime placeholder and production Grafana reconciliation can recover.

### Out Of Scope

- Changing alert rules, notification policy, datasource configuration, secrets, or capacity thresholds.
- The separate private repository Arr fix, tracked by `homelab-private` pull request 43.

## Requirements

- **FR-001**: Flux strict post-build substitution MUST not require a `DS_LOKI` cluster variable.
- **FR-002**: The dashboard MUST retain its Grafana runtime `DS_LOKI` datasource reference after rendering.
- **FR-003**: No alert expression, routing policy, Secret, or consumer reference may change.

## Success Criteria

- **SC-001**: Strict production rendering succeeds without a `DS_LOKI` substitution value.
- **SC-002**: Production `Kustomization/flux-system/grafana` reaches `Ready=True` after the merged revision is applied.
- **SC-003**: The Flux failing and readiness-unknown alerts resolve after the dependent Kustomizations recover.

## Assumptions

- `$${DS_LOKI}` is Flux's literal-dollar escape and renders as Grafana's `${DS_LOKI}` placeholder.
