# PR Smoke Gate Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** A required `dev-smoke` check proves testable PRs in the dev cluster on an ephemeral runner pod, and Renovate bumps of whoami and homepage auto-merge when it is green.

**Architecture:** ARC runner pods in the dev cluster run the existing verifier (`--ci` mode) from a `pull_request_target` workflow that checks out `main` only. Classification and the required aggregator run on GitHub-hosted runners. Auto-merge is a Renovate package rule, enabled last.

**Tech Stack:** Python 3 (stdlib, unittest), GitHub Actions, Actions Runner Controller (runner scale set), Flux, Playwright 1.56.1, Renovate, `gh` CLI.

**Spec:** `docs/superpowers/specs/2026-11-15-pr-smoke-gate-design.md`

## Global Constraints

- Runner scale set: `minRunners: 0`, `maxRunners: 1` (the maximum is the lock). Name `homelab-dev` (used as `runs-on`).
- Slug is `pr-<PR number>`; route `whoami-pr-<N>.dev.lab.petebeegle.com`. Same-repo PRs only: `github.event.pull_request.head.repo.full_name == github.repository` on every job.
- Trigger `pull_request_target`; the smoke job checks out `main` only and passes the PR as data (`--branch <head ref>`, via an env var, never interpolated into a shell line). Workflow token `contents: read`, `pull-requests: read`. No path filters on the workflow.
- Playwright version is one value in `tests/browser/package.json` and the runner image base tag (`mcr.microsoft.com/playwright:v1.56.1-noble`); they must match.
- v1 auto-merge class is **whoami and homepage only**, never major updates. Renovate automerge stays off until `dev-smoke` is a required check.
- Dev kubeconfig only; never touch production. Do not stage or print tfvars (the CI path does not use Terraform).
- Stdlib-only Python, tests with `unittest` in `tools/development/tests/` (existing style: `FakeRunner`, no cluster needed). `python3 tools/verification/verify.py --profile harness` must stay green after every task.
- Commit style: conventional commits, ending with `Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>`.

## Review Focus

1. A fork PR reaches the dev runner: every job in `dev-smoke.yml` carries the same-repo condition (pinned by a static test in Task 7).
2. Empty or huge changed-file list: empty means *not tested* ("no changes"); a list over the API's page size is read with `--paginate` (Task 3 test for empty; workflow uses pagination).
3. A PR touches two apps, or an app plus anything else: *not tested* with a reason, never a partial smoke (Task 3).
4. Homepage has no browser block: `--browser` is passed only when the profile has one (Task 3 output `browser`, Task 7 uses it).
5. A cancelled run leaves a `pr-<N>` environment behind: the job deletes leftovers first, and a scheduled sweep removes old ones (Task 4).
6. Renovate rule and the profiles drift apart: a test compares them (Task 10). Playwright image and `package.json` drift: a test compares them (Task 5).

---

## File Structure

- Delete: `tools/development/runner/`, `.github/workflows/whoami-browser-smoke.yml`, `docs/runbooks/ephemeral-dev-runner.md`, `docs/runbooks/whoami-browser-ci.md`, `specs/{ephemeral-dev-runner,runner-hardening,browser-ci-contract}/`.
- Modify: `tools/development/devverify/{cli,config,workflow}.py`, `tools/development/smoke-profiles/{whoami,homepage}.json`, `tools/verification/verify.py`, `renovate.json`, `AGENTS.md`.
- Create: `tools/development/classify_pr.py`, `tools/development/cleanup_pr_envs.py`, `tools/ci/runner-image/Dockerfile`, `.github/workflows/{dev-smoke,dev-cleanup,dev-heartbeat,runner-image}.yml`, `kubernetes/infra/controllers/arc/`, `kubernetes/apps/dev-runner/`, `kubernetes/clusters/development/infra/arc.yaml`, `kubernetes/clusters/development/apps/dev-runner.yaml`, tests under `tools/development/tests/`, and `docs/superpowers/specs/2026-11-15-process-layer-audit.md`.

## Phases and gates

A (repo only): Tasks 1-4. B (needs owner): Task 0, then 5, 6. C: Task 7 (informational, observe on real PRs). D: Tasks 8-10 in this order only (heartbeat, then required, then Renovate rule). E: Tasks 11-12.

---

### Task 0: Owner prerequisites (not code; blocks Task 6)

Verified against GitHub's current "Authenticate to the API" page for ARC: for **repository-level** runners a GitHub App needs repository permission **Administration: Read and write** and **Metadata: Read-only**. The organization "Self-hosted runners" permission applies only to org-owned installs, not this user-owned repo.

- [ ] **Step 1: Create the GitHub App** (GitHub, Settings, Developer settings, GitHub Apps, New GitHub App). GitHub App name `homelab-dev-arc`; Homepage URL `https://github.com/petebeegle/homelab`; **Webhook: Active unchecked**; no callback URL; Repository permissions: Administration = Read and write, Metadata = Read-only (automatic); no organization or account permissions; no event subscriptions; "Where can this GitHub App be installed": Only on this account.
- [ ] **Step 2: Generate a private key** on the App's page (a `.pem` downloads); note the **App ID** shown on the App page.
- [ ] **Step 3: Install the App** on `petebeegle/homelab` only (choose "Only select repositories"). The **installation ID** is the number at the end of the URL `https://github.com/settings/installations/<ID>` after installing.
- [ ] **Step 4: Store in 1Password**, in the development vault (`cluster development`), one item with exactly these field labels (they become the Kubernetes secret keys ARC reads): `github_app_id`, `github_app_installation_id`, `github_app_private_key` (the full multi-line PEM). Find the path pieces with `op item list --vault "cluster development"` and `op item get <item> --format json`; the plan needs `vaults/<vault-uuid>/items/<item-uuid>`.
- [ ] **Step 5:** Give the agent the App ID, installation ID and the 1Password item path (none is a secret). **Never paste the private key anywhere.**
- [ ] **Step 6:** Set the fork-PR approval policy: `gh api -X PUT repos/petebeegle/homelab/actions/permissions/fork-pr-contributor-approval -f approval_policy=all_external_contributors`, then GET to confirm.

Alternative (simpler, less safe): a fine-grained PAT with Administration: Read and write on this repo only, stored as one field `github_token`. It grants the same power as the App but is long-lived (expires within a year, tied to your account) where the App issues short-lived tokens. A classic PAT (`repo` scope) is broader still and not recommended.

Blast radius to know: Administration lets the holder change this repo's settings, rulesets, collaborators and deploy keys. The key lives only in the dev vault and the `dev-runner` namespace's secret; it is read by the ARC controller and listener, **not** mounted into job pods.

### Task 1: Delete the superseded runner work

**Files:** delete the paths in File Structure; modify `tools/verification/verify.py` (drop the runner test line from `PROFILES["harness"]`); update any doc or test that references the deleted paths.

**Interfaces:** Produces: a repo with no `tools/development/runner`, `whoami-browser-smoke.yml`, or their docs and specs.

- [ ] **Step 1:** `git grep -n -E 'development/runner|whoami-browser-smoke|ephemeral-dev-runner|whoami-browser-ci'` and list every reference outside the files being deleted.
- [ ] **Step 2:** Delete the files; fix each reference found (remove or repoint; `docs/runbooks/harness-golden-path.md` keeps working without them).
- [ ] **Step 3:** Run `python3 tools/verification/verify.py --profile harness` (expect exit 0) and `git grep` again (expect no output).
- [ ] **Step 4:** Commit `chore: remove superseded ephemeral runner work`. Close #449 and #453 with a comment pointing at the design.

### Task 2: `--ci` mode for the verifier

**Files:** modify `tools/development/devverify/{cli,config,workflow}.py`; test in `tools/development/tests/test_verify_branch_deploy.py`.

**Interfaces:** Produces: `AppConfig.ci: bool = False` (CLI `--ci`); `run_acceptance` with `config.ci` skips `run_terraform` and first calls `assert_dev_base_ready(config, *, runner) -> None` in `devverify/flux.py`, which raises `VerificationError("development base is not healthy: <names>")` unless Kustomizations `flux-system` and `gateway` in `flux-system` are Ready=True (use the existing `kubectl`/`run_command` helpers).

- [ ] **Step 1:** Tests: `test_ci_skips_terraform_and_checks_base_first` (commands contain no `terraform`, and a `get kustomization` for `gateway` precedes the activation `apply`); `test_ci_unhealthy_base_fails_before_activation` (FakeRunner reports `gateway` not Ready; expect `VerificationError`, no `apply` command, no cleanup); `test_ci_flag_is_documented` (extend the existing flag-docs test list with `--ci` and add it to `tools/development/README.md`).
- [ ] **Step 2:** Run the three; expect FAIL.
- [ ] **Step 3:** Implement as specified; keep default behavior unchanged without `--ci`.
- [ ] **Step 4:** Run the whole `test_verify_branch_deploy.py` and the harness profile; expect pass.
- [ ] **Step 5:** Commit `feat(dev): add --ci mode to the branch verifier`.

### Task 3: PR classifier

**Files:** create `tools/development/classify_pr.py`; modify `tools/development/smoke-profiles/{whoami,homepage}.json` (add `"prSmoke": true`) and `devverify/profiles.py` + `config.py` (`SmokeProfile.pr_smoke: bool = False`); test `tools/development/tests/test_classify_pr.py`.

**Interfaces:** Produces: `classify(changed_files: Sequence[str], profiles: Mapping[str, SmokeProfile]) -> Classification` with `Classification(tested: bool, app: str | None, browser: bool, reason: str)`; CLI `python3 tools/development/classify_pr.py` reads file paths from stdin (one per line) and prints one JSON object with those four keys.

Rules (*tested* only if all hold): non-empty; every file is under `kubernetes/apps/<app>/` for the **same** single app; that app's profile has `pr_smoke`; no file under `terraform/`, `tests/browser/`, `tools/development/`. `browser` is true iff the profile has a `browser` block. Otherwise `tested=False` with a specific `reason`.

- [ ] **Step 1:** Tests, each asserting the full `Classification`: single whoami file is tested with `browser=True`; homepage file is tested with `browser=False`; two apps is not tested ("multiple apps"); whoami plus `README.md` is not tested; `terraform/x.tf` alone is not tested; `tools/development/devverify/cli.py` is not tested; an app without `pr_smoke` (jellyfin) is not tested; empty list is not tested ("no changes"); CLI round-trip prints valid JSON.
- [ ] **Step 2:** Run; expect FAIL (module missing).
- [ ] **Step 3:** Implement; profile loading reuses `load_smoke_profiles()`; add the `prSmoke` field with validation (boolean, default false).
- [ ] **Step 4:** Run the new tests and the existing `test_verify_branch_deploy.py`; expect pass.
- [ ] **Step 5:** Commit `feat(dev): classify PRs for dev smoke`.

### Task 4: Stale environment cleanup

**Files:** create `tools/development/cleanup_pr_envs.py`; test `tools/development/tests/test_cleanup_pr_envs.py`.

**Interfaces:** Produces: `cleanup_pr_envs(*, kubeconfig: Path, slug: str | None, older_than_seconds: int | None, runner=subprocess.run) -> list[str]` returning the names it deleted. CLI `--kubeconfig`, `--slug pr-12` (delete that slug's objects), `--older-than 3h` (delete all `pr-*` environments older than that). It deletes the Flux `Kustomization` named `branch-*-pr-<N>` and `GitRepository` `branch-pr-<N>` in `flux-system` (and waits for the namespace), never anything whose slug does not match `^pr-[0-9]+$`.

- [ ] **Step 1:** Tests with a FakeRunner returning canned `kubectl get -o json`: `--slug pr-12` deletes only `pr-12` objects; `--older-than 3h` deletes only objects older than 3h; an object named `branch-whoami-smoke` or `branch-main` is never touched; nothing to delete returns `[]` and exits 0.
- [ ] **Step 2:** Run; expect FAIL. **Step 3:** Implement (reuse `devverify.kube.kubectl`/`run_command`). **Step 4:** Run; expect pass.
- [ ] **Step 5:** Commit `feat(dev): clean up stale PR environments`.

### Task 5: Runner image

**Files:** create `tools/ci/runner-image/Dockerfile`, `.github/workflows/runner-image.yml`; test `tools/development/tests/test_runner_image.py`.

**Interfaces:** Produces: image `ghcr.io/petebeegle/homelab-dev-runner:<sha>` (also `:latest`), based on `mcr.microsoft.com/playwright:v1.56.1-noble`, containing the Actions runner at `/home/runner`, kubectl, the Flux CLI, Python 3 and Node (from the base). Pinned versions via build args that Renovate can update.

- [ ] **Step 1:** Test `test_playwright_versions_match`: the Dockerfile's base tag version equals the version in `tests/browser/package.json` (read both, assert equal).
- [ ] **Step 2:** Run; expect FAIL. **Step 3:** Write the Dockerfile so the test passes; the runner runs as a non-root user.
- [ ] **Step 4:** Workflow builds on push to `main` touching `tools/ci/runner-image/**` and on `workflow_dispatch`, pushes to GHCR, and runs a smoke step in the built image: `kubectl version --client`, `flux --version`, `npx --no-install playwright --version`, each exit 0.
- [ ] **Step 5:** Commit; after merge confirm the workflow run is green and the package is pullable from the dev cluster.

### Task 6: ARC in the dev cluster

**Files:** create `kubernetes/infra/controllers/arc/` (namespace, HelmRepository of type OCI for the ARC charts, controller HelmRelease, `kustomization.yaml`); `kubernetes/apps/dev-runner/` (namespace, runner-scale-set HelmRelease, `ServiceAccount` + `Role`/`ClusterRole` + bindings, `OnePasswordItem` for the App credentials, `kustomization.yaml`); `kubernetes/clusters/development/infra/arc.yaml` and `kubernetes/clusters/development/apps/dev-runner.yaml` (copy the shape of `metrics-server.yaml`/`whoami.yaml`; the app `dependsOn` the controller and `onepassword-operator`); add both to the cluster `kustomization.yaml` lists.

**Interfaces:** Consumes: Task 5 image; Task 0 credentials item. Produces: a runner scale set `homelab-dev` in namespace `dev-runner`.

Values pinned by the spec: `githubConfigUrl: https://github.com/petebeegle/homelab`, `minRunners: 0`, `maxRunners: 1`, image from Task 5, `/dev/shm` as a memory-backed `emptyDir` (start at 1Gi), pod runs as non-root with `allowPrivilegeEscalation: false` and `capabilities.drop: [ALL]`. RBAC: in `flux-system` create/get/list/watch/delete `gitrepositories` and `kustomizations`; cluster-wide get/list/watch on `namespaces`, `pods`, `services`, `persistentvolumeclaims`, `httproutes`, `helmreleases`; create/delete pods in branch namespaces (the verifier's probe pods). No `secrets` access unless a profile check proves it needs it.

- [ ] **Step 1:** Pin chart versions (look up current ARC chart versions; pick ones at least two weeks old). Write the manifests; `kubectl kustomize` each directory (expect it renders) and run the repo's `kubernetes` CI checks locally if available.
- [ ] **Step 2:** Open as a PR; after merge, on dev: `kubectl -n dev-runner get helmrelease,pods` shows both HelmReleases Ready and the listener pod Running (expected output: Ready True, Running).
- [ ] **Step 3:** Prove the pod can do the job: a throwaway workflow_dispatch run on `runs-on: homelab-dev` executes `kubectl get kustomization -n flux-system` and `npx --no-install playwright --version` successfully, then the runner pod disappears.

### Task 7: `dev-smoke` workflow (informational)

**Files:** create `.github/workflows/dev-smoke.yml`; test `tools/development/tests/test_dev_smoke_workflow.py` (static YAML-text checks, stdlib only).

**Interfaces:** Consumes: Tasks 2, 3, 4, 6. Produces: check name `dev-smoke` (the aggregator job's `name`).

Jobs: `classify` (`ubuntu-latest`; `gh api --paginate repos/${{ github.repository }}/pulls/<N>/files --jq '.[].filename'` piped to `classify_pr.py`, checked out from `main`; outputs `tested`, `app`, `browser`, `reason`); `smoke` (`needs: classify`, `if: needs.classify.outputs.tested == 'true'`, `runs-on: homelab-dev`, `timeout-minutes: 20`; checkout `ref: main`, `persist-credentials: false`; write a kubeconfig from the pod's ServiceAccount; run `cleanup_pr_envs.py --slug pr-<N>`; run `verify_branch_deploy.py --ci --app $APP --branch "$HEAD_REF" --slug pr-<N>` plus `--browser` only if `browser == 'true'`, with `HEAD_REF` taken from an env var; upload `tests/browser/test-results` and `browser-results` with `if: always()`); `dev-smoke` (`ubuntu-latest`, `needs: [classify, smoke]`, `if: always()`; passes if `smoke` succeeded or `tested != 'true'` and writes "not smoke-tested: <reason>" to the job summary; fails otherwise).

- [ ] **Step 1:** Tests: `test_trigger_is_pull_request_target_without_path_filters`; `test_every_job_requires_same_repo` (each job's `if` contains `head.repo.full_name == github.repository`; the aggregator's condition combines it correctly with `always()`); `test_concurrency_group_is_per_pr_and_cancels`; `test_smoke_job_checks_out_main_only` (`ref: main`, no `github.event.pull_request.head` in any `with:`); `test_head_ref_is_passed_via_env` (no `${{ github.event.pull_request.head.ref }}` inside a `run:` block).
- [ ] **Step 2:** Run; expect FAIL. **Step 3:** Write the workflow. **Step 4:** Run; expect pass; run the repo's workflow lint via pre-commit.
- [ ] **Step 5:** Commit. Merge it as **not required**. Then prove on real PRs, recording each result in the PR description: (a) a same-repo PR changing only the whoami image tag runs the smoke and passes (and the dev environment is gone afterwards); (b) a docs-only PR reports "not smoke-tested"; (c) a PR touching `terraform/` reports not tested; (d) a PR with a deliberately broken whoami manifest fails and cleans up; (e) two PRs at once queue behind each other and both finish.

### Task 8: Heartbeat

**Files:** create `.github/workflows/dev-cleanup.yml` (schedule every 30 min, `runs-on: homelab-dev`, runs `cleanup_pr_envs.py --older-than 3h`) and `.github/workflows/dev-heartbeat.yml` (schedule hourly, `ubuntu-latest`).

**Interfaces:** Produces: the heartbeat fails (GitHub emails on a failed scheduled run) when `dev-cleanup` has not succeeded in the last 2 hours, i.e. the runner or dev cluster is down. This replaces the design's Grafana alert because dev has no monitoring stack.

- [ ] **Step 1:** Add a static test that both workflows exist with the stated schedules and that the heartbeat queries the last successful `dev-cleanup` run time and fails past 2 hours.
- [ ] **Step 2:** Implement. **Step 3:** Verify by scaling the ARC controller to 0 in dev for ~2 hours (or temporarily lowering the threshold in a test run) and confirming the heartbeat fails; restore.
- [ ] **Step 4:** Commit.

### Task 9: Make `dev-smoke` required

Preconditions: Task 7's five proofs recorded; Task 8 verified; at least a week of stable runs.

- [ ] **Step 1:** Update the ruleset: add `{ "context": "dev-smoke", "integration_id": 15368 }` to `required_status_checks` in `.github/rulesets/main-required-checks.json` and apply with `gh api -X PUT repos/petebeegle/homelab/rulesets/27289884 --input .github/rulesets/main-required-checks.json`.
- [ ] **Step 2:** Verify: the API shows three required checks; an open PR that has `dev-smoke` green still shows mergeable; update `docs/runbooks/main-branch-protection.md`.

### Task 10: Renovate auto-merge for whoami and homepage

**Files:** modify `renovate.json`; test `tools/development/tests/test_renovate_automerge.py`.

**Do this only after Task 9** (before it, automerge would merge on `Pre-commit` and the harness alone).

- [ ] **Step 1:** Test `test_automerge_apps_match_pr_smoke_profiles`: the app names in the automerge `packageRules` `matchFileNames` equal the set of profiles with `prSmoke: true`; `test_automerge_excludes_major_updates`.
- [ ] **Step 2:** Run; expect FAIL. **Step 3:** Add one package rule: `matchFileNames` for `kubernetes/apps/whoami/**` and `kubernetes/apps/homepage/**`, `matchUpdateTypes: ["minor","patch","digest","pin"]`, `automerge: true`. **Step 4:** Run; expect pass; validate with `npx --yes --package renovate renovate-config-validator renovate.json` if available.
- [ ] **Step 5:** Verify on the next real Renovate PR for whoami or homepage: `dev-smoke` runs, then the PR merges by itself, and the push CI runs on `main`. If the merge does not trigger CI on `main`, record it and decide with the owner.

### Task 11: Trim the agent instructions

**Files:** modify `AGENTS.md`.

- [ ] **Step 1:** Replace the invariant that requires validating through the dev cluster before PR completion with: the `dev-smoke` check is the gate for apps with a profile; for everything else run `verify_branch_deploy.py --browser` by hand. Remove any line this makes redundant. Do not touch SOPS, Gateway or Talos rules.
- [ ] **Step 2:** Run `python3 tools/verification/verify.py --profile harness` and the repo's pre-commit. Commit.

### Task 12: Process-layer audit (read-only deliverable)

**Files:** create `docs/superpowers/specs/2026-11-15-process-layer-audit.md`.

- [ ] **Step 1:** For each of `.codex/hooks/*`, `.agents`, `.specify`, `tools/codex-harness`, `tools/context-pack`, `tools/agent-memory`, `tools/foundry_bluegreen_pkg`, `tools/nexus`, `tools/vpn`, `tools/onepassword`: read it, `git grep` for references, and record in a table: purpose, who calls it, keep/delete/decide, evidence. Keep the SOPS guard.
- [ ] **Step 2:** Commit and hand the table to the owner; deletions are separate PRs after the owner decides.

---

## Self-review notes

Spec coverage: pods (6), image (5), workflow incl. same-repo/no-path-filter/classify/aggregate (7), slug (7), Renovate auto-merge (10), stale cleanup (4, 8), fork guard (0), health instead of Grafana alert (8, deviation noted), cleanup (1), audit (12), AGENTS.md (11), rollout order and gating (9 before 10). Not in this plan by design: promotion, other apps, network policy, second App.
