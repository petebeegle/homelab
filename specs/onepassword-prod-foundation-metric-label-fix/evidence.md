# Evidence: 1Password Alert Metric Label Fix

**Base**: `origin/main` at `77e0405083f8e6d03b34833f9cd314dcb641afba`

## Discovery

- Kubernetes Deployment: desired `1`, available `1`.
- Direct kube-state-metrics endpoint: desired `1`, available `1`, resource label `namespace="onepassword-system"`.
- Mimir series: desired `1`, available `1`, labels `namespace="monitoring"` and `exported_namespace="onepassword-system"`.
- Merged alert expression result: `1` through its absent branch.
- Item-unready expression before canary: `0`.

## Validation

- TDD red: the exported-resource-namespace regression failed against merged main.
- Focused policy tests: PASS, 4 tests.
- Production foundation policy: PASS.
- Alert render and kubeconform 0.7.0: zero invalid/errors; Grafana CR schemas unavailable and skipped.
- Full pre-commit suite: PASS.
- Exact corrected expression evaluated against live Mimir before merge: `0` for the healthy `1/1` operator.
- Convergence audit found no missing repository task; post-merge reconciliation remains.
