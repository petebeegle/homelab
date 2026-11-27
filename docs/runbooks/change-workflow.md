# Change Workflow

How a change gets from an idea to `main`, what checks it, and how to get past a
broken check. The reasoning is in [decisions.md](../decisions.md#changes-go-through-pull-requests-and-the-check-is-the-evidence).

## Procedure

1. **Branch.** Never commit to `main`. Create a worktree so parallel sessions do
   not collide:

   ```sh
   git fetch origin main
   git worktree add .codex/tmp/worktrees/<name> -b codex/<name> origin/main
   ```

2. **Design, if the change is big enough to need one.** Write the design and plan
   in a GitHub issue or the PR description, not in the repo, and get the owner's
   approval of the design before building. Small changes skip this.
3. **Test first.** Where the change has testable behavior, write the failing
   test, watch it fail, then write the code.
4. **Check locally.**

   ```sh
   python3 tools/verification/verify.py --profile harness
   pre-commit run --all-files
   ```

5. **Open the PR.** In the description, say what you validated and how.
6. **Let the checks run** (below).
7. **Merge** when the required checks pass. If a required check itself is broken,
   see [Break glass](#break-glass).

## What checks a PR

| Check | Required | What it does |
|-------|----------|--------------|
| `Pre-commit` | yes | `pre-commit run --all-files`: YAML lint, manifest validation, `terraform fmt` and docs, the generated architecture doc, policy checks |
| `Verification / harness` | yes | `python3 tools/verification/verify.py --profile harness`: runs every Python and Node test it discovers under `tools/`, except a short excluded list in `verify.py` |
| `Flux render` | yes | `flux-local test --enable-helm` on `kubernetes/clusters/production`: builds every Flux Kustomization production runs, with `cluster-vars` substituted, and templates every HelmRelease with its pinned chart. Catches missing chart versions, values a new chart rejects, broken kustomize builds and remote bases. Proves it renders, not that it runs |
| `dev-smoke` | not yet (issue #477) | Deploys the change to the development cluster and tests it, when the PR qualifies (below) |

The harness is deliberately not a browser or cluster check. It proves the tools
and manifests render; it does not prove anything runs. That is what `dev-smoke`
and your own development validation are for. A new test file under `tools/` is
picked up automatically.

### What `dev-smoke` covers, and what it does not

`dev-smoke` tests a PR in one of two ways.

- **App smoke** (`smoke` job): every changed file is under one
  `kubernetes/apps/<app>/` directory and that app's profile in
  `tools/development/smoke-profiles/` has `"prSmoke": true` (today: `whoami`,
  `homepage`, `home-assistant`, `jellyfin`, `immich` and
  `nexus`). It publishes GitHub's merge of the PR onto current `main` as the
  temporary branch `pr-smoke/pr-<N>`, creates a branch environment from it in
  the development cluster, checks it with the profile from `main`, runs the
  browser test where the profile has one, and removes the environment and the
  branch. Deploying the merge, not the PR head, keeps a head that is behind
  `main` from being judged by `main`'s probes against the old app.
- **Base smoke** (`base` job): the PR changes something the development cluster
  itself runs. `tools/development/affected_dev.py` decides by rendering each
  development Flux Kustomization at `main` and at GitHub's merge of the PR onto
  `main` (so a change through a shared base or patch counts, and a
  production-only path does not). `tools/development/base_smoke.py` then:
  1. publishes that merge as the temporary branch `base-smoke/pr-<N>`;
  2. suspends development's root Kustomization and points every child at that
     branch;
  3. waits for every Kustomization and HelmRelease to be Ready;
  4. runs the whoami and homepage smoke tests (from `main`) on top as canaries;
  5. always restores `main` and deletes the branch.

  A PR that changes development's Flux bootstrap (`flux-system/`),
  `cluster-vars.yaml` or entrypoint is refused, and so is one GitHub cannot merge
  onto current `main` (rebase it). If a killed job leaves the root suspended,
  `dev-cleanup` and every smoke run restore it after an hour
  (`base_smoke.py --recover-stale`).

For everything else it reports "not smoke-tested: <reason>" and passes. The
exception is a Renovate PR (`renovate/*` branch) inside Renovate's auto-merge
paths: `dev-smoke` fails it instead, so Renovate cannot merge it on a green that
tested nothing (see [Renovate](renovate.md#auto-merge)). Passing does not mean
the change needs no validation. For Terraform, production-only
infrastructure and apps, Flux bootstrap changes, and apps without a profile:

- validate in the development cluster before merging, and
- state in the PR description what you ran and what it showed.

If the development cluster or its credentials are unavailable, say so and list
the substitute checks. A real validation failure is not an exception: fix it and
rerun.

### When `dev-smoke` fails

1. Open the failed run's `smoke` job. The verifier prints which step failed
   (Flux reconcile, pods, Service, route, probe, browser). Playwright traces and
   screenshots are attached to the run as artifacts.
2. Decide whether the change or the development base is at fault. The job first
   waits for the development base Kustomizations to be Ready; a failure there
   means development itself is unhealthy, not your PR. Check with
   `kubectl --kubeconfig ~/.kube/homelab-development.config -n flux-system get kustomization`.
3. If the change is at fault, fix it and push. The next run replaces the
   environment. A run removes its own environment when it ends, then removes
   any other `pr-*` environment older than three hours that a cancelled run
   left behind, including the PVs their claims left Released; `dev-cleanup`
   does the same on a schedule. A failed sweep is a
   warning on the run, not a smoke failure.
4. If development is at fault, fix development first (it is changed through PRs
   like production), then re-run the failed job. A `base` failure that says
   `DEVELOPMENT DID NOT RECOVER` means development is still broken after the
   restore: check `kubectl -n flux-system get kustomization` and
   `flux resume kustomization flux-system` before anything else runs.
5. To see it yourself, deploy the same branch by hand with `--keep` (below),
   inspect it, then delete it with
   `python3 tools/development/cleanup_pr_envs.py --kubeconfig ~/.kube/homelab-development.config --slug <slug>`
   (the slug must start with `pr-`; for other slugs delete the
   `branch-<app>-<slug>` Kustomization and `branch-<slug>` GitRepository).

`dev-heartbeat` runs on a GitHub-hosted runner and fails when no job on the
`homelab-dev` runner (`dev-cleanup`, or a `dev-smoke` `smoke` job) has succeeded
in 12 hours, which means the runner (in production, namespace `ci-runner`) or
the development cluster is down. A red heartbeat usually explains a burst of red
or stuck smoke runs.

## Smoke-testing by hand

```sh
python3 tools/development/verify_branch_deploy.py \
  --app <app> --branch <branch> --slug <slug> --kubeconfig ~/.kube/homelab-development.config
```

Add `--ci` to skip the Terraform step and wait for the development base to be
healthy first. The branch must be pushed. The verifier removes the environment
when it finishes; add `--keep` to leave it for inspection.

### Browser check

Add `--browser` for apps whose profile has a browser test. It runs Playwright
against the deployed route through development DNS, TLS and the Gateway, so it
checks what a user would reach, not just Kubernetes objects. You need Node and
npm, Chromium (and its OS libraries), development DNS reachable, and the
development certificate trusted:

```sh
npm --prefix tests/browser install --no-save --package-lock=false
(cd tests/browser && npx playwright install chromium)
npm --prefix tests/browser run test:unit
python3 tools/development/verify_branch_deploy.py --app whoami --branch <branch> --slug <slug> --browser
```

To run the browser test alone against a kept environment:

```sh
WHOAMI_URL=https://whoami-<branch_slug>.dev.lab.petebeegle.com npm --prefix tests/browser test
```

- **Pass:** the browser reached the route over trusted HTTPS and got the
  expected response.
- **Fail:** navigation, TLS, HTTP, content or an unexpected redirect.
- **Not run:** no environment, DNS, Chromium or dependencies. Report it as
  unverified, never as a pass.

It does not prove Authentik, network policy, production routing or
infrastructure-wide correctness.

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

## Branch protection on `main`

Repository ruleset `main-required-checks` (id `27289884`) requires
`Verification / harness`, `Pre-commit` and `Flux render` to pass before a merge. All are pinned
to the GitHub Actions app (`integration_id` 15368), so no other app can report a
passing status under those names. Branches need not be up to date and no
approving review is required. The rule file at
`.github/rulesets/main-required-checks.json` is a record only; GitHub does not
read it from the repository.

Not covered: required reviews, force-push or deletion protection, signed
commits, a merge queue. Add them deliberately.

### Break glass

Repository admins can bypass the ruleset only when merging a pull request. Direct
pushes to `main` stay blocked, so every override leaves a PR trail. Use it only
when a required check is wrong or broken (the CI itself is down, or a check fails
for a reason unrelated to the change) and waiting is worse than the risk:

```sh
gh pr merge <number> --merge --admin
```

Afterwards, say in the PR why the bypass was needed and open a follow-up to fix
the check. Do not use it to skip a check that is correctly failing.

### Changing the ruleset

It is managed through the GitHub API, not Terraform:

```sh
gh api repos/petebeegle/homelab/rulesets/27289884            # inspect
gh api -X PUT repos/petebeegle/homelab/rulesets/27289884 --input .github/rulesets/main-required-checks.json
```

Check names must match the check-run names exactly. Renaming a job in a workflow
silently makes the old required name unsatisfiable and blocks every merge until
the ruleset is updated (or bypassed).
