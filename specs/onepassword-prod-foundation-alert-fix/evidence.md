# Evidence: onepassword-prod-foundation-alert-fix

**Base**: `origin/main` at `330d634c58a4909d10cbb6ed8bee23dd605f9785`

## Discovery

- Production operator Kustomization: Ready at the merged revision.
- HelmRelease: Ready, chart `2.4.1`.
- Live Deployment: `onepassword-connect-operator`, desired `1`, available `1`, image `1password/onepassword-operator:1.12.0`.
- Incorrect alert target: `onepassword-operator`.
- Grafana alert CR was absent because its Flux Kustomization had not yet advanced past a transient Gateway dependency wait; the incorrect rule did not become active.

## Validation

- TDD red: the new live-name regression test failed against merged main and showed all three incorrect PromQL selectors.
- Focused policy tests: PASS, 3 tests.
- Production foundation policy checker: PASS.
- Alerting Kustomize render: PASS, 10 resources.
- kubeconform 0.7.0: zero invalid/errors; all 10 Grafana custom resources skipped for unavailable schemas.
- Architecture check: PASS; architecture output is unaffected.
- Full pre-commit suite: PASS.
- Convergence audit: no missing repository task; only post-merge live reconciliation remains.
