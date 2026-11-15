# Runner hardening — specification

## Intent
Close the concrete lifecycle and image gaps found by review of #448 and by the live smoke (specs/harness-live-smoke), without claiming a live Proxmox run.

## Acceptance
- An overall deadline bounds every lifecycle step, teardown included.
- SIGTERM/SIGINT run teardown; a second SIGTERM cannot interrupt it.
- Cloning onto an existing VMID is refused; a VM is destroyed only after its config shows this run's ownership marker and expected name.
- Cleanup steps are independent, never mask the primary failure, and report a possibly leaked VM.
- The GitHub runner registration is removed best-effort; registration tokens never appear in ssh argv, and GitHub API errors never echo response bodies.
- ssh host/guest aliases are validated and passed after `--`.
- `prepare-vm.sh` installs Chromium OS libraries (pinned to the repo's Playwright version) and installs `run-once.sh` at the path `lifecycle.py` executes.
- Written records match the code. Tests model failures, and each protection is proven by a mutation that makes a specific test fail.

## Non-goals
Live Proxmox execution; building the template image; network ACLs; a scheduled stale-VM sweeper; per-run runner labels (needs a workflow change in #447); changing branch protection.
