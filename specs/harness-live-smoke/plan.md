# Harness live smoke — plan

SDD tier: low. Workflow risk: low (temporary, self-cleaning development-cluster objects; docs-only repository change).
Smoke strategy: this implementation *is* the smoke. A driver script outside the repository reuses `tools/development/devverify` (activate, reconcile, assert, cleanup in `finally`) and runs the Playwright spec against `https://whoami-smoke.dev.lab.petebeegle.com`.
Fanout: two read-only reviewers (runner lifecycle gaps on #448; written-record drift on #447/#448) ran in parallel with the live run. No tracked edits were fanned out.
Exceptions:
- `terraform init/validate/plan` (first step of `run_acceptance`) skipped: needs the ignored `terraform.tfvars` and credentials that are not in the worktree, and the tested branch is unmodified `main`. Recorded in `evidence.md`.
- Worktree placed under `.codex/tmp/worktrees/` because `/workspaces` was not writable (AGENTS.md allows sibling-clone fallbacks; this is the repository's ignored scratch area).
Human gate: the user approved running the live smoke and then committing the evidence ("A then B"). Spec/plan/task checkpoints are combined under the low-risk exception.
