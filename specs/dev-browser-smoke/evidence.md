# Evidence — dev browser smoke command

Date: 2026-11-15. Base: `origin/main` @ `bdb1802`. Status: **VERIFIED live from the devcontainer against the development cluster; NOT verified from a GitHub Actions runner.**

## Unit tests

- `python3 tools/verification/verify.py --profile harness`: exit 0.
- `tools/development/tests/test_verify_branch_deploy.py`: 41 tests pass (8 new, covering command ordering, cleanup after browser failure and timeout, preflight before any cluster command, a profile with no browser check, profile validation, off-by-default).
- Mutation check (scratch script, bytecode caching disabled): removing each protection made a specific test fail, 6/6: no preflight, browser step skipped, `--no-install` dropped, missing-Playwright ignored, no-browser-profile allowed, spec path traversal allowed.

## Live run (the real CLI)

Command: `TF_VAR_talos_version=v1.12.1 python3 tools/development/verify_branch_deploy.py --app whoami --branch main --slug smoke --browser --timeout 10m`

| Run | Result |
| --- | --- |
| 1 | Failed closed at `terraform plan`: `talos_version` has no default on `origin/main` and is not in tfvars. Nothing was activated; no leftover objects in dev. |
| 2 | Exit 0. Sequence: `terraform init`, `validate`, `plan`, `kubectl apply` (branch activation), `flux reconcile source git branch-smoke`, `flux reconcile kustomization branch-whoami-smoke`, cluster-side assertions, `env WHOAMI_URL=https://whoami-smoke.dev.lab.petebeegle.com npx --no-install playwright test tests/whoami.spec.cjs` (1 passed), cleanup (Kustomization, namespace, GitRepository deleted). |

After run 2: no `smoke` GitRepository, Kustomization or namespace remained in the development cluster. Development kubeconfig only; no `--terraform-apply`, no `--push`, no production access.

## Caveats (not hidden)

- **The Terraform plan is not a drift signal here.** Development state is a local file (`terraform/development/terraform.tfstate`) in the main checkout; the worktree had none, so the plan saw empty state (`Plan: 12 to add`). The step only proved that init, validate and plan execute with the staged inputs. Plan exit code 2 is accepted by the verifier by design.
- **`talos_version`** was supplied via `TF_VAR_talos_version=v1.12.1` (read from the live dev node's OS image). On clean `main` the variable has no default; an in-flight branch (`upgrade-talos-oom-fix`) adds one. Not changed here.
- `terraform.tfvars` was staged under `.codex/tmp/implementation-secrets/dev-browser-smoke/` and installed into the worktree per AGENTS.md; contents were never printed, and both copies are git-ignored and were removed afterwards.
- Tested unmodified `main` from the devcontainer, so it proves the mechanism, not a particular change. Whoami is the only app with a browser check.
- Chromium and its OS libraries were installed manually in this container earlier in the session (see specs/harness-live-smoke/evidence.md); the command only checks that Playwright is installed, and relies on Playwright failing if the browser is missing.

## Branch protection

Ruleset `main-required-checks` (id 27289884) applied through the API and read back: `required_status_checks` = `Verification / harness`, `Pre-commit` (both pinned to the GitHub Actions app); bypass = repository admin role, `pull_request` mode only (`current_user_can_bypass: pull_requests_only`). A direct push to `main` was deliberately **not** attempted to test it. Documented in docs/runbooks/main-branch-protection.md.
