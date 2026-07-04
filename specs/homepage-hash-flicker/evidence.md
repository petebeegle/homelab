# Evidence: Homepage Hash Flicker

**Branch**: `codex/homepage-hash-flicker`
**Risk Tier**: medium
**Started**: 2026-07-04

## Spec Kit Initialization

- Command: Manual Spec Kit artifact bootstrap following
  `docs/runbooks/spec-driven-development.md` and
  `docs/runbooks/implementation-workflow.md`.
- Outcome: PASS
- Spec Kit version: Not changed by this implementation.
- Integration: Existing repo Codex integration.
- Fallback: `/workspaces/homelab-worktrees` was not writable, so the dedicated
  worktree was created at
  `/workspaces/homelab/.codex/tmp/worktrees/homepage-hash-flicker`.

## Workflow Validation

| Command | Result | Notes |
| ------- | ------ | ----- |
| `git fetch origin && git worktree add /workspaces/homelab-worktrees/homepage-hash-flicker -b codex/homepage-hash-flicker origin/main` | FAIL | `/workspaces/homelab-worktrees` could not be created: permission denied. |
| `git worktree add /workspaces/homelab/.codex/tmp/worktrees/homepage-hash-flicker -b codex/homepage-hash-flicker origin/main` | PASS | Fallback dedicated worktree created on `codex/homepage-hash-flicker` at `35b1785`. |
| `python3 tools/codex-harness/validate_sdd_context.py --root "$(pwd)" --branch "$(git branch --show-current)" --require-plan-artifacts` | PASS | No output; exit code 0. |
| `git commit -m "fix: stabilize homepage hash responses"` | PASS | Created `1256f583de9270cc34b0a981e99a1adcb612cd47`; pre-commit hooks passed, including `yamllint`, `k8svalidate`, and generated architecture check. |
| `git push origin HEAD:refs/heads/codex/homepage-hash-flicker` | PASS | Branch pushed to origin. |

## Local Checks

| Command | Result | Notes |
| ------- | ------ | ----- |
| `env -i PATH="$PATH" HOME="$HOME" cluster_domain=lab.petebeegle.com homepage_target_domain=lab.petebeegle.com bash -c 'kubectl kustomize kubernetes/apps/homepage | flux envsubst --strict'` | PASS | Rendered to `/tmp/homepage-hash-flicker-prod.yaml`. |
| `env -i PATH="$PATH" HOME="$HOME" cluster_domain=dev.lab.petebeegle.com homepage_target_domain=lab.petebeegle.com bash -c 'kubectl kustomize kubernetes/apps/homepage/development | flux envsubst --strict'` | PASS | Rendered to `/tmp/homepage-hash-flicker-dev.yaml`. |
| Rendered `Deployment/homepage` replica assertion | PASS | Production and development renders both reported `Deployment/homepage replicas=1`. |
| `git diff --check` | PASS | No whitespace errors. |
| `python3 tools/architecture/render.py --check` | PASS | No output; exit code 0. |

## Automated Smoke And Live Verification

| Target | Method | Result | Notes |
| ------ | ------ | ------ | ----- |
| `https://homepage.lab.petebeegle.com/` | `curl -k -sS -L --max-redirs 8` | PASS pre-change | Returned `code=200 redirects=0 url=https://homepage.lab.petebeegle.com/ type=text/html; charset=utf-8`. |
| `https://homepage.lab.petebeegle.com/api/hash` | Repeated curl over 75 seconds and a later 20-request sample | FAIL pre-change | Returned two unique hashes. Later 20-request sample returned 11 responses for `92123b128cb010f36cba1d09b85a33f0f3b55abe568121cd75248e71f72f1eaa` and 9 for `cdcb93fef29440bea0d268147ef991d04d0365da9ad236bddb339343ff0834f8`. |
| Browser reload behavior | Static client bundle inspection | PASS diagnostic | Homepage client compares `/api/hash`, calls `/api/revalidate`, then `window.location.reload()` when the hash changes. |
| `codex/homepage-hash-flicker` | `python3 tools/development/verify_branch_deploy.py --app homepage --branch codex/homepage-hash-flicker --slug homepage-hash-flicker --push` | FAIL then PASS | First attempt pushed the branch but failed Terraform plan because ignored development tfvars were absent from the worktree. After staging and installing `terraform/development/terraform.tfvars` without logging contents, rerun passed. |

## Deployment State

- Source fetched SHA: Development Flux fetched
  `codex/homepage-hash-flicker@sha1:1256f583de9270cc34b0a981e99a1adcb612cd47`.
- Target applied SHA: Development Kustomization applied
  `codex/homepage-hash-flicker@sha1:1256f583de9270cc34b0a981e99a1adcb612cd47`.
- Live resource spec checked: Pre-change exact live spec not available because
  no kube context is configured in this shell.
- Gateway/listener/DNS/certificate checked: Existing route left unchanged;
  pre-change curl proved the exact URL reaches Homepage.
- Exact user-facing URL result: Pre-change `https://homepage.lab.petebeegle.com/`
  returned HTTP `200` with no redirects. Post-merge verification remains
  required after Flux applies the PR.

## Development Validation

- Profile: homepage
- Branch slug: homepage-hash-flicker
- HEAD: `1256f583de9270cc34b0a981e99a1adcb612cd47`
- Report path: Inline command output from
  `python3 tools/development/verify_branch_deploy.py --app homepage --branch codex/homepage-hash-flicker --slug homepage-hash-flicker --push`.
- Cleanup: PASS; verifier deleted
  `Kustomization/branch-homepage-homepage-hash-flicker`, waited for
  `namespace/homepage-homepage-hash-flicker` deletion, and deleted
  `GitRepository/branch-homepage-homepage-hash-flicker`.
- Result or exception: PASS after installing the ignored development
  `terraform.tfvars` into the worktree through
  `.codex/tmp/implementation-secrets/homepage-hash-flicker/` without logging
  secret contents. Terraform init/validate/plan completed, Flux fetched and
  applied the branch, the branch namespace became Active, the branch pod became
  Ready, Service and HTTPRoute checks ran, and the in-cluster HTTP probe matched
  `Home Lab|Branch|Homepage`.

## Documentation Impact

- Updated: `specs/homepage-hash-flicker/`
- Generated docs: Not expected.
- No-docs rationale: Replica-count-only workload fix; behavior and HA tradeoff
  are captured in implementation artifacts.

## SDD Conformance

- Local sources checked: `AGENTS.md`,
  `docs/runbooks/spec-driven-development.md`,
  `docs/runbooks/implementation-workflow.md`,
  `.specify/memory/constitution.md`.
- Upstream Spec Kit sources checked: Existing local Spec Kit templates and
  skills.
- Spec -> Plan -> Tasks -> Implement alignment: PASS.
- Artifact updates after implementation: PASS.

## Exceptions And Follow-Ups

- Dedicated worktree fallback used because `/workspaces/homelab-worktrees` was
  not writable in this environment.
- First development verifier attempt failed because ignored development
  Terraform variables were not present in the worktree; rerun passed after
  workflow-compliant staging and installation.
- Post-merge live hash stability must be verified after Flux applies the PR.

## Final State

- Final branch: `codex/homepage-hash-flicker`
- Final HEAD: `1256f583de9270cc34b0a981e99a1adcb612cd47` for the
  smoke-verified implementation commit; this evidence update may create a
  follow-up commit without changing rendered manifests.
- Commit: `1256f583de9270cc34b0a981e99a1adcb612cd47`
