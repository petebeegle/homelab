---
status: active
scope:
  - github
authority: operational
created: 2026-11-15
---

# `main` branch protection and break glass

## What is enforced

Repository ruleset `main-required-checks` (id `27289884`, applied 2026-11-15) on the default branch requires these GitHub Actions checks to pass before a merge:

- `Verification / harness` (the shared `tools/verification/verify.py --profile harness` contract)
- `Pre-commit` (`pre-commit run --all-files`; this replaced the per-edit agent hook)

Both are pinned to the GitHub Actions app (`integration_id` 15368), so no other app can report a passing status under those names. Branches need not be up to date, and no approving review is required. The rule file is kept at `.github/rulesets/main-required-checks.json` as a record; GitHub does not read it from the repository.

## Break glass

Repository admins (role id 5) can bypass the ruleset, **only when merging a pull request**. Direct pushes to `main` stay blocked, so every override leaves a PR trail.

Use it only when a required check is wrong or broken (for example the CI itself is down, or a check is failing for a reason unrelated to the change) and waiting is worse than the risk:

```bash
gh pr merge <number> --merge --admin
```

Afterwards: say in the PR why the bypass was needed, and open a follow-up to fix the check. Do not use it to skip a check that is correctly failing.

## Changing it

The ruleset was created and is managed through the GitHub API, not Terraform:

```bash
gh api repos/petebeegle/homelab/rulesets/27289884            # inspect
gh api -X PUT repos/petebeegle/homelab/rulesets/27289884 --input .github/rulesets/main-required-checks.json
```

Check names must match the check-run names exactly. Renaming a job in a workflow silently makes the old required name unsatisfiable and blocks every merge until the ruleset is updated (or bypassed).

## Not covered

No required reviews, force-push or deletion protection, signed commits, or merge queue. Add them deliberately; they are not implied by this ruleset.
