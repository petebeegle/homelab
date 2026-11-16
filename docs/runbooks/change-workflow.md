# Change Workflow

How a change gets from an idea to `main`. The rule behind this is
`docs/decisions/pr-gated-change-workflow.md` (ADR-0016).

## Procedure

1. **Branch.** Never commit to `main`. Create a worktree so parallel sessions do
   not collide:

   ```sh
   git fetch origin main
   git worktree add /workspaces/homelab-worktrees/<name> -b codex/<name> origin/main
   ```

2. **Design, if the change is big enough to need one.** Put the design under
   `docs/superpowers/specs/` and the plan under `docs/superpowers/plans/`, and get
   the owner's approval of the design before building. Small changes skip this.
3. **Test first.** Where the change has testable behavior, write the failing
   test, watch it fail, then write the code.
4. **Check locally.**

   ```sh
   python3 tools/verification/verify.py --profile harness
   pre-commit run --all-files
   ```

5. **Open the PR.** In the description, say what you validated and how.
6. **Let the checks run.** `Pre-commit` and `Verification / harness` are
   required. `dev-smoke` deploys and tests the change in the development cluster
   when the PR changes only an app with a smoke profile.
7. **Merge** when the required checks pass. The break-glass path is in
   `docs/runbooks/main-branch-protection.md`.

## What `dev-smoke` covers, and what it does not

`dev-smoke` tests a PR when every changed file is under one
`kubernetes/apps/<app>/` directory and that app's profile in
`tools/development/smoke-profiles/` has `"prSmoke": true` (today: `whoami` and
`homepage`). It creates a branch environment in the development cluster, checks
it, runs the browser test where the profile has one, and removes the
environment.

For everything else it reports "not smoke-tested: <reason>" and passes. That
does not mean the change needs no validation. For Terraform, Flux wiring,
infrastructure, Gateway routes, storage, secret references, and apps without a
profile:

- validate in the development cluster before merging, and
- state in the PR description what you ran and what it showed.

If the development cluster or its credentials are unavailable, say so and list
the substitute checks. A real validation failure is not an exception: fix it and
rerun.

## Smoke-testing by hand

```sh
python3 tools/development/verify_branch_deploy.py \
  --app <app> --branch <branch> --slug <slug> --kubeconfig ~/.kube/homelab-development.config
```

Add `--browser` for apps with a browser check (needs Playwright; see
`docs/runbooks/harness-golden-path.md`). Add `--ci` to skip the Terraform step
and wait for the development base to be healthy first. The branch must be
pushed. The verifier removes the environment when it finishes.

## Worktrees that need local secrets

Ignored files such as `terraform.tfvars` and kubeconfigs do not exist in a new
worktree. Stage them once from the main checkout and install them where needed,
without printing their contents:

```sh
# in the main checkout
.codex/scripts/stage_implementation_secrets.sh <name>
# in the worktree
.codex/scripts/install_implementation_secrets.sh <name>
```

## Adding an app to `dev-smoke`

1. Build `kubernetes/apps/<app>/branch/` as a kustomize overlay on the app's
   real manifests (see `whoami` and `homepage`). Do not copy manifests into it.
2. Add or update the app's profile in `tools/development/smoke-profiles/` and
   set `"prSmoke": true`.
3. Add the app to `REAL_DIRS` in
   `tools/development/tests/test_branch_overlay_render.py`.
4. Prove it on two throwaway PRs: one that edits only the real manifest must
   pass, and one that breaks only the real manifest must fail and leave the
   development cluster clean.
