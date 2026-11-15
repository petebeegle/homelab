# Evidence — runner hardening

Date: 2026-11-15. Base: #448 head `e89e4c9` (branch `codex/ephemeral-dev-runner`). Status: **MOCK-VERIFIED ONLY. No live Proxmox, ssh, GitHub registration or process-death behavior was exercised.**

## Verified

- `python3 tools/verification/verify.py --profile harness`: exit 0 (includes `tools/development/runner/tests`, 14 tests, plus the browser URL-guard tests, 8/8).
- Mutation check (scratch script, bytecode caching disabled): each protection was removed in turn and the matching test failed. 7/7 caught: ownership check, free-VMID precheck, stop-failure isolation, ssh `--` terminator, deadline enforcement, registration cleanup, token-in-argv.
  - A first run of this check gave a misleading row because Python reused a stale `.pyc` (two mutations had the same size and mtime second). It was rerun with `-B`; only the corrected run is counted.
- `bash -n prepare-vm.sh`: ok. The Playwright version expression resolves to `1.56.1` from `tests/browser/package.json`.

## Not verified

- `prepare-vm.sh` execution (needs root on a disposable Ubuntu VM): untested. The need for the OS libraries is evidenced by the live smoke (21 missing libraries) in specs/harness-live-smoke; the install command itself matches what ran there (`playwright install-deps chromium`) but not at the pinned version via `npx`.
- Real `qm` output formats: the fake assumes `qm config` prints `name:` and `description:` lines. A live run must confirm the ownership check matches (Proxmox may URL-encode description text; the marker is hex so it should survive).
- SIGTERM during a real ssh child; SIGKILL/OOM/host loss (still leaks; needs the sweeper).
- GitHub registration deletion against the real API (needs `administration` scope on the admin token).

## Known remaining gaps

Scheduled sweeper; per-run label (#447 workflow change); per-VM guest host-key pinning (clones from one template share a key, so pinning does not authenticate a specific VM); network ACLs; concurrent leases on the same VMID are prevented only by the free-VMID check, which is not atomic across two simultaneous runs; the registration token is briefly visible in the guest's process list during `config.sh`.

## Scope notes

Records corrected: runbook (status, boundary, template/orchestration text), #448 plan/tasks/evidence. #447's records (CI pending, `--with-deps` in its workflow) are on that branch and were not edited here.
