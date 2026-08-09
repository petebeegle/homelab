# Feature Specification: 1Password Alert Metric Label Fix

**Branch**: `codex/onepassword-prod-foundation-metric-label-fix`
**Created**: 2026-08-09
**Status**: Approved corrective follow-up
**Risk Tier**: high

## Summary

Correct the operator availability alert to filter kube-state-metrics resource identity by `exported_namespace="onepassword-system"`. Live Mimir evaluation showed Alloy attaches `namespace="monitoring"` to the scrape target and preserves the Kubernetes resource namespace as `exported_namespace`; the merged rule therefore took its absent branch and returned `1` for a healthy operator.

## Requirements

- **FR-001**: All operator desired, available, and absent selectors MUST use `exported_namespace="onepassword-system"`.
- **FR-002**: The rule MUST evaluate to `0` while the live Deployment is available `1/1`.
- **FR-003**: The regression test and policy checker MUST reject `namespace="onepassword-system"` for these kube-state-metrics series.
- **FR-004**: No credential, SOPS, consumer, operator, or item-readiness behavior may change.

## Acceptance

- Focused policy/pre-commit checks pass.
- Corrected rule reconciles from merged main.
- Exact live operator expression returns `0`; item expression returns `0` before the canary.

The user's instruction to complete the production foundation authorizes this bounded correction. Live labels remove any design ambiguity.
