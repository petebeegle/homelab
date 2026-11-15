# PR smoke gate: design

Date: 2026-11-15. Status: approved by the owner in conversation ("update the design and get at it"); this file records it.

## Intent

Prove a pull request in the development cluster before it merges, and let proven Renovate bumps of a small set of apps merge themselves. The point is to take work off the agents: today they carry hooks, Spec Kit ceremony and manual dev validation. If CI proves the change, they can stop. Longer arc: dev-to-prod promotion, then comprehensive smoke coverage. This document covers the first step only: **gate the merge**.

## Goals

- A required check `dev-smoke` that runs `verify_branch_deploy.py --browser` for testable PRs, on an ephemeral runner pod inside the dev cluster.
- Renovate bumps of **whoami and homepage** auto-merge when `dev-smoke` is green. Nothing else auto-merges.
- Concurrent PRs queue safely.
- The repo gets smaller: the superseded runner/VM work is deleted in the same effort.

## Non-goals

Dev-to-prod promotion, merge queue, Terraform-changing PRs, forks, jellyfin/immich/nexus/home-assistant coverage (they join once they pass in dev on a real PR), network-policy hardening, Proxmox VMs, the local-model work from #449.

## Anti-goals

A "not tested" pass being mistaken for proof; fork-PR code running on the LAN; more process files than before.

## Observed constraints

- Dev is one Talos node (4 CPU, 23 GB, about 5 GB and 38% CPU used), long-lived, Flux following `main`. Pods resolve `*.dev.lab.petebeegle.com`. Cilium is present.
- The verifier (`tools/development/devverify`) activates a per-branch Flux `GitRepository` and `Kustomization`, asserts, runs the browser spec, and cleans up. It always passes `--kubeconfig <file>` to kubectl/flux. Its Terraform step needs ignored tfvars and local state, and `talos_version` has no default on `main`.
- Chromium ran in a dev pod as non-root, default seccomp, all capabilities dropped, sandbox on, and loaded a dev route (HTTP 200) using `mcr.microsoft.com/playwright:v1.56.1-noble` (one page; default 64 MB `/dev/shm`).
- The `main` ruleset requires `Verification / harness` and `Pre-commit` only; admin bypass through PRs only. Repo auto-merge is now **enabled** (2026-11-15); no PR has it requested. Fork PR approval policy is `first_time_contributors`; default workflow token permission is read-only.
- Renovate runs self-hosted (a CronJob under `kubernetes/apps/renovate`, in production) and its PRs are authored by the owner's account; branches are `renovate/*`, the only label is `dependencies`. `renovate.json` has no automerge rules, and no automerge setting exists in the Renovate app config.
- The repo is **public**.
- Dev secrets come from a development-only vault read by a read-only service account.

## Approaches considered

1. **Gate the merge only (chosen).** Smoke in dev, then merge; Flux applies `main` to dev and prod together. Simplest. Does not catch two PRs that pass alone and break together.
2. **Gate the merge and gate prod (next).** Post-merge smoke on dev's `main`, and prod follows a promoted ref. The end goal; not built yet.
3. **Merge queue.** Tests the combined result and serializes merges, but does not gate prod. Revisit only if "breaks together" bites.

## Design

1. **Runner pods (GitOps).** Actions Runner Controller in runner-scale-set mode in the dev cluster, ephemeral pods, minimum 0 and maximum **1**. The maximum is the lock: dev hosts one smoke at a time. Added as a dev-only app under the development cluster entrypoint. Credential: **one GitHub App**, installed on this repo only, key supplied by the dev 1Password operator. In-cluster ServiceAccount gives the job cluster access; it can create and delete Flux `GitRepository`/`Kustomization` objects and read and create pods and services in branch namespaces. Accepted consequence: creating Flux Kustomizations is effectively cluster-admin in dev, tolerable because dev is disposable and the workflow comes from `main`.
2. **Runner image.** Official Playwright image plus the Actions runner, kubectl, the Flux CLI and Python, built and published to GHCR by a workflow in this repo, version-pinned, kept current by Renovate. The Playwright version in the image and in `tests/browser/package.json` move together.
3. **Workflow `dev-smoke`**, trigger `pull_request_target` (so the workflow always comes from `main`), runs for **every** PR with no path filters (a path-filtered required check that does not run blocks the PR forever). Three jobs:
   - `classify` on a GitHub-hosted runner: reads the changed-file list through the API, checks out nothing. Decides *tested* (every changed file is under a profiled app's directory and nothing under `terraform/**`, `tests/browser/**` or `tools/development/**` changed) or *not tested*.
   - `smoke` on the dev runner pod, only if *tested*: checks out `main` only, passes the PR as data (`--branch <head ref>`), runs the verifier with a new `--skip-terraform` flag, uploads Playwright traces and a summary. Slug `pr-<number>`.
   - `dev-smoke` on a GitHub-hosted runner, `needs` both, `if: always()`, the single required check. Passes if `smoke` succeeded or the PR was *not tested* (the summary says "not smoke-tested: reason"); fails if `smoke` failed, was cancelled or timed out.
   - Concurrency group per PR number with cancel-in-progress, so a new push supersedes the old run. Queueing across PRs is the runner pool's job; a concurrency group keeps only one pending run and cancels the rest. Same-repo PRs only: every job is conditioned on `head.repo.full_name == github.repository`.
4. **Auto-merge is Renovate's job, in config.** `renovate.json` gets a package rule turning on `automerge` (GitHub platform auto-merge) for whoami and homepage updates that are not major. GitHub then merges when the required checks pass; the merge comes from the owner's token, so follow-up workflows run. A PR outside the rule never gets auto-merge, so a "not tested" pass cannot merge unattended. A human can still enable auto-merge by hand.
5. **Stale environments.** A cancelled job may not clean up. The job first deletes any leftover `pr-<N>` objects (idempotent), and a periodic cleanup removes `pr-*` environments with no open PR or older than a few hours.
6. **Fork guard.** Set the Actions fork-PR approval policy to all outside contributors **before** the runner goes live. This plus the same-repo condition is the whole security story for the public repo.

### Rollout

1. Delete the inert runner work (below); land the runner, image and workflow as an **informational** check; run it on real PRs.
2. Make `dev-smoke` required, but only after a Grafana alert for runner/dev health exists (otherwise a broken dev silently blocks merges); add the Renovate automerge rule.
3. Widen the class as profiles prove out in dev; then approach 2.

Escape hatch if the runner or dev is down: the ruleset's admin-via-PR bypass.

## Cleanup in this effort

The repo is bloated: `specs/` is 337 files in 66 directories (the cluster config in `kubernetes/` is 380); agent-harness directories (`.codex`, `.specify`, `.agents`, `.claude`) add 68; `tools/` has 124. Delete only with evidence nothing references it and CI green; git history is the archive.

- **In this effort:** delete the inert runner work (`tools/development/runner/`, `.github/workflows/whoami-browser-smoke.yml`, `docs/runbooks/ephemeral-dev-runner.md`, `docs/runbooks/whoami-browser-ci.md`, and the matching `specs/`); close #449 and #453 as superseded; produce a keep/delete audit table for `.codex/hooks/*`, `.agents`, `.specify`, `tools/codex-harness`, `tools/context-pack`, `tools/agent-memory` and the one-off packages under `tools/`. Contents of most of these have not been read; nothing is claimed about them beyond their existence.
- **Decided later, by the owner:** ending the per-PR `specs/<implementation>/` requirement (it changes AGENTS.md, an ADR and the constitution), trimming AGENTS.md and `.claude/rules`, and archiving old specs.

## Calls I made (correct any)

Runner pods in dev rather than prod; `pull_request_target` with a `main` checkout; `pr-<N>` slug; one runner at a time; classify and aggregate on GitHub-hosted runners; custom runner image on the Playwright base; one GitHub App; Renovate (not the workflow) enables auto-merge, for whoami and homepage only; `dev-smoke` required only after a health alert exists; this doc lives in `docs/superpowers/specs/` (the repo's validators expect `specs/<implementation>/` for pushes; the builder reconciles, ideally by deleting that requirement later).

Dropped from the earlier draft as disproportionate for a homelab: runner and branch-namespace network policies, a second GitHub App, workflow-enabled auto-merge and its labels, per-VM Proxmox firewalling.

## Unverified, to check while building

- ARC authenticates with a GitHub App or a classic PAT ([docs](https://docs.github.com/en/actions/how-tos/manage-runners/use-actions-runner-controller/authenticate-to-the-api)); the App's repository permissions are now confirmed from GitHub's page (Administration: Read and write, Metadata: Read-only; see Task 0 of the plan); the chart's min/max runner values names are still unconfirmed.
- Renovate's platform auto-merge works with this self-hosted setup, and the merge triggers the push CI on `main`.
- Chromium in the runner pod was tested with one page via `playwright-core`, not the test runner or a heavy app; `/dev/shm` may need enlarging.
- The verifier works with a ServiceAccount-derived kubeconfig; the RBAC list is a starting point.
- Creating the GitHub App is a manual owner step (browser); the plan cannot complete without it.

## Left to the builder

ARC chart versions and layout under `kubernetes/`; runner image build workflow; RBAC manifests; the changed-files-to-profile classifier; `--skip-terraform` and its refusal on Terraform paths; stale-environment cleanup mechanism; the 1Password item declaration; the Renovate rule; the audit tables.
