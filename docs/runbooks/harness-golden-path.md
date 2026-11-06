---
status: draft
scope:
  - development-cluster
  - codex-harness
authority: operational
created: 2026-11-06
last_verified: 2026-11-06
---

# Golden-path browser verification: Whoami

The existing branch deployment verifier proves Kubernetes/Flux resource behavior. This opt-in Playwright suite adds **user-path** verification through development DNS, TLS, and Gateway. It does not deploy anything or modify the cluster.

## Prerequisites
- Development cluster and DNS are reachable from the machine running Playwright.
- A dedicated Whoami branch environment was deployed and remains active for the browser check.
- Node/npm and Chromium are installed; the test environment must trust the development certificate.

## Run
From a checkout on `codex/harness-golden-path`:

```bash
npm --prefix tests/browser install --package-lock-only
npm --prefix tests/browser ci
npm --prefix tests/browser exec -- playwright install chromium
npm --prefix tests/browser run test:unit
```

Deploy a disposable Whoami branch environment using the existing `tools/development/verify_branch_deploy.py` with `--keep` (check its CLI help and the development-cluster runbook for exact flags). After reconciliation, run:

```bash
WHOAMI_URL=https://whoami-<branch_slug>.dev.lab.petebeegle.com \
  npm --prefix tests/browser test
```

Record actual exit codes, branch SHA, development smoke report, Playwright JUnit XML and failure traces in the implementation evidence. Clean up branch resources using the existing development runbook after browser verification.

## Interpretation
- **Pass**: browser reached a development Whoami route over trusted HTTPS and verified a Whoami response.
- **Fail**: navigation, TLS, HTTP, content, or unexpected redirect check failed.
- **Not run / blocked**: no environment, DNS, Chromium, or dependencies; must be reported as unverified, not pass.

This test does not prove Authentik, Cilium policy isolation, production routing, or infrastructure-wide correctness. It is the first layer of a broader verification harness.
