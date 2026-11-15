# Tasks

- [x] Confirm the devcontainer reaches the development cluster and DNS (read-only).
- [x] Create a dedicated worktree from `origin/main`.
- [x] Install Playwright, Chromium, headless shell, FFMPEG and Chromium OS libraries.
- [x] Run URL guard unit tests (8/8 pass).
- [x] Run live activation, cluster-side assertions, browser smoke and cleanup (run 2 pass; run 1 failure recorded).
- [x] Verify no `smoke` resources remain in the development cluster.
- [x] Record results, exceptions and environment findings in `evidence.md`.
- [ ] Re-run under Node 24 to confirm or rule out the Playwright extraction hang.
- [ ] Run the full `verify_branch_deploy.py` including Terraform plan where the ignored tfvars exist.
- [ ] Run the same smoke from a GitHub Actions runner once one exists (#447/#448).
