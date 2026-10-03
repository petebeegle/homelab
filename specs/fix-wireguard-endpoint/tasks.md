# Tasks: fix-wireguard-endpoint

- [x] T001 Confirm current WAN address, encrypted value, and stored profile host.
- [x] T002 Reproduce stale-host reconciliation with a disposable database.
- [x] T003 Update encrypted endpoint and existing startup reconciliation.
- [x] T004 Verify preservation, idempotency, manifest rendering, and encryption.
- [x] T005 Run available development validation and document user-path limits.
- [x] T006 Update runbook and converge artifacts for PR handoff.

Analysis: each task maps to FR-001 through FR-004; changes are sequential and
preserve the single implementation/branch/PR contract.

- [x] T007 [P] Independent read-only review; consolidate findings in evidence.
