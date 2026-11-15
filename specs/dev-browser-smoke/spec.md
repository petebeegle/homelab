# Dev browser smoke command — specification

## Intent
Give agents and humans one command that deploys a branch to the development cluster, verifies it cluster-side, loads the real route in a browser, and cleans up. This is the local equivalent of a PR check, available before any CI runner exists.

## Acceptance
- `verify_branch_deploy.py --app whoami --branch B --slug S --browser` runs the existing verifier, then the Playwright spec named by the profile against the first rendered route URL, then cleanup.
- Missing Playwright, spec, or a profile without a browser check is reported as unverified and fails before anything is deployed; cleanup still runs after a browser failure or timeout.
- Browser checks are declared per profile (`browser: {spec, urlEnv}`) with validated names; no path traversal, no arbitrary env names.
- Off by default; existing behavior is unchanged without `--browser`.
- Docs match the code; the main branch requires `Verification / harness` and `Pre-commit` with an admin-via-PR break glass.

## Non-goals
Running this from GitHub Actions (needs the runner), generic multi-route browser checks, changing the Whoami spec, fixing the Terraform step's local-state and `talos_version` assumptions.
