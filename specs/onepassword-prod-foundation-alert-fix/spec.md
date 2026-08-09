# Feature Specification: 1Password Production Alert Selector Fix

**Feature Branch**: `codex/onepassword-prod-foundation-alert-fix`
**Created**: 2026-08-09
**Status**: Approved corrective follow-up
**Risk Tier**: high

## Summary

Correct the production 1Password operator-unavailable alert and runbook to target the live Helm-generated Deployment name `onepassword-connect-operator`. Phase-2 post-merge validation found the operator healthy at `1/1` under that name before the Grafana alert group reconciled, so the incorrect rule never became active.

## Scope

### In Scope

- Replace the incorrect Deployment selector in the PromQL alert.
- Update operator diagnosis/rollout commands to use the live name.
- Strengthen the production-foundation policy test so the selector cannot regress.
- Reconcile Grafana only after the corrected rule merges.

### Out Of Scope

- Operator, token, vault, SOPS, consumer, or canary changes.
- Any change to alert duration, severity, or item-readiness logic.

## Requirements

- **FR-001**: The operator-unavailable rule MUST query `onepassword-connect-operator` for desired, available, and absent Deployment cases.
- **FR-002**: Repository policy MUST reject the former `deployment="onepassword-operator"` selector.
- **FR-003**: Runbook rollout and log commands MUST reference the live Deployment.
- **FR-004**: Local render/policy/pre-commit checks and live Grafana reconciliation MUST pass before the production phase is considered healthy.

## Success Criteria

- **SC-001**: The regression test fails on merged main and passes after the correction.
- **SC-002**: The live Grafana `onepassword` alert group reconciles successfully from the corrected main revision.
- **SC-003**: The healthy live operator does not satisfy the unavailable query.

## Gate Status

The user's instruction to continue the production phase authorizes this necessary bounded correction. No clarification is required because the live Deployment identity is authoritative.
