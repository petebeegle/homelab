# Tasks

- [x] Add optional `browser` block to smoke profiles; validate it; declare it for Whoami.
- [x] Add `--browser` to the CLI; preflight before activation; run after assertions, before cleanup.
- [x] Tests: ordering, failure and timeout cleanup, preflight, no-browser profile, validation, off-by-default.
- [x] Mutation-check each protection (6/6 caught).
- [x] Update README and runbooks; add the main branch-protection runbook and ruleset record.
- [x] Apply the ruleset (required checks, admin bypass via PR only) and read it back.
- [x] Run the full real command against development (exit 0, cleanup verified).
- [ ] Give the Terraform step a default `talos_version` (in flight on `upgrade-talos-oom-fix`) and decide how CI gets state.
- [ ] Run this command from a GitHub Actions runner (needs the runner infrastructure).
