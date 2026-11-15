# Evidence — live Whoami golden-path smoke (development)

Date: 2026-11-15. Source: `origin/main` @ `ac54370` (includes #444, #445, #446). Worktree: `.codex/tmp/worktrees/harness-live-smoke` (branch `codex/harness-live-smoke`; `/workspaces` was not writable, so the repo's scratch dir was used).

State: **VERIFIED for the development cluster-side path and the browser path, run from the devcontainer. NOT verified from a GitHub Actions runner or the disposable runner VM (#447/#448).**

## What ran (run 2, passing)

Driver: a scratch script outside the repo that calls the existing `tools/development/devverify` functions in the same order as `run_acceptance`:
`render_activation_template` → `apply_activation` → `reconcile_flux` → `assert_smoke_profile` → Playwright → `cleanup_branch_environment` (in `finally`).

| Step | Result | Time |
| --- | --- | --- |
| Activation applied (`branch-smoke` GitRepository on `main`, `branch-whoami-smoke` Kustomization) | ok | 0.2s |
| Flux reconcile | ok | 21.2s |
| Cluster-side profile assertions (Kustomization, Service, HTTPRoute for `whoami-smoke`) | PASSED | 21.8s |
| `npx playwright test tests/whoami.spec.cjs` against `https://whoami-smoke.dev.lab.petebeegle.com` | 1 passed, exit 0 | 23.7s |
| Cleanup (Kustomization, namespace, GitRepository deleted) | completed | 32.1s |

Post-run check: no `smoke` GitRepository, Kustomization or namespace remained in the dev cluster. Dev kubeconfig only (`~/.kube/homelab-development.config`). No production access, no pushes, no Terraform apply.

JUnit written to `tests/browser/browser-results/junit.xml`; failure traces are retained by config but none were produced on the passing run.

## Run 1 (failed, recorded for honesty)

Cluster-side assertions passed (19.9s). The browser step failed with `chromium_headless_shell` missing (Playwright 1.56 uses a separate headless binary). The page was never loaded. Cleanup completed and left nothing behind. Fixed by installing the missing browser binaries (below), then re-run as run 2.

## Exceptions and deviations (not hidden)

- **Terraform step skipped.** `run_acceptance` runs `terraform init/validate/plan` on `terraform/development` first. That needs the git-ignored `terraform.tfvars` plus state/provider credentials, which are not in this worktree. The branch under test is unmodified `main`, so no Terraform drift check was relevant to this smoke. Substitute: none. The full `verify_branch_deploy.py` command was therefore **not** run end to end.
- **Deployed `main`, not a feature branch.** This proves the harness path, not a specific change.
- **Run from the devcontainer, not a runner.** It proves the browser test and URL guard work against the real Gateway/TLS when run from inside the dev network. It does not prove #447's workflow or #448's disposable VM.
- **Not independently re-verified:** the `whoami.dev...` (non-branch) permanent route; certificate chain beyond what Chromium accepted with `ignoreHTTPSErrors: false`.

## Environment findings (feed into runner image work)

1. **Chromium needs OS libraries.** The downloaded Chromium failed to start with 21 missing shared libraries (NSS, ATK, CUPS, xcb, etc.) until `playwright install-deps chromium` ran as root. The runner VM image must include them; neither `prepare-vm.sh` (#448) nor an unprivileged job installs them.
2. **Playwright's archive extraction hangs here.** `npx playwright install chromium` downloaded fully, then stalled during extraction (reproduced 3 times, on 2 MB to 182 MB archives; killed at timeout). Manual `unzip` into `~/.cache/ms-playwright/<dir>/` plus an `INSTALLATION_COMPLETE` marker worked. Container Node is v26.13.1; CI pins Node 24.21.0. Node version is the suspected cause but **not tested**.
3. `playwright install chromium` fetches three artifacts: Chromium, FFMPEG and Chromium Headless Shell. All three were required.

## Follow-ups

- Confirm or rule out Node 26 as the extraction-hang cause (retry under Node 24).
- Run the same smoke via #447's workflow on a real runner once one exists.
- Run the full `verify_branch_deploy.py` including Terraform plan from an environment that has the ignored tfvars.
- Pre-existing dev cluster items noticed, not touched: stale `branch-homepage-homepage-dashboard` GitRepository failing for ~175 days (branch deleted); `local-path-provisioner` Kustomization stuck "Reconciliation in progress".
