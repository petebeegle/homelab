# Harness live smoke — specification

## Intent
Produce the first real, recorded execution of the Whoami golden path from #444 against the development cluster, so later harness work (#447 workflow, #448 runner) builds on observed behavior and not on unit tests alone.

## Acceptance
- A temporary development branch environment for Whoami is activated, reconciled by Flux, and passes the existing cluster-side smoke-profile assertions.
- The browser smoke (`tests/browser/tests/whoami.spec.cjs`) loads the exact HTTPS route in real Chromium and passes.
- The temporary environment is removed afterwards and the removal is verified.
- Every deviation from the full `verify_branch_deploy.py` command is recorded in `evidence.md`, and failed runs are recorded alongside passing ones.
- No production access, no Terraform apply, no GitOps manifest changes, no pushes of test branches.

## Non-goals
Changing any harness code, the #447 workflow, the #448 runner, or branch protection. Fixing the issues the run uncovers; those are follow-ups.
