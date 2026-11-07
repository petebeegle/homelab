# Tasks: Hybrid AI harness handoff

Risk: low / docs-only. Input: spec.md and plan.md in this directory.
User authorization covers preparing and opening this plan PR only. Implementation remains for the receiving code agent.

## Documentation deliverable

- [x] T001 [FR-001] Inspect main, #444–#448, relevant workflow runs and open PR inventory.
- [x] T002 [FR-002] Write staged plan with source paths, acceptance and recovery requirements.
- [x] T003 [FR-003] Review constitution, private-network, credential and no-merge constraints.
- [ ] T004 [FR-004] Validate artifacts, publish draft PR, verify it remains unmerged.

## Receiving code agent: execution checklist

- [ ] Refresh main, PR heads/checks/reviews and actual environment access; do not treat this snapshot as live status.
- [ ] Reconcile #447/#448 descriptions and evidence with code; inspect lifecycle timeout/ownership/cleanup gaps.
- [ ] Resolve the prior GitGuardian report associated with commit 0272e66 through current alert/rotation evidence. Do not print secret values or assume removing text revoked credentials. This handoff has not re-audited that incident.
- [ ] Create a named infrastructure implementation and prove the full private runner lifecycle and failure cleanup.
- [ ] Implement one durable supervisor job with restart/lease/revision correctness before broad agent autonomy.
- [ ] Confirm hardware ownership, supported OS/GPU/runtime and management access; implement reproducible appliance provisioning.
- [ ] Add interchangeable local/hosted providers, external policy enforcement and bounded escalation.
- [ ] Establish evaluations, promotion/rollback, observability, backup and recovery evidence.
- [ ] Convert each recurring failure into a reviewed check/recovery improvement where justified.

Each phase follows plan.md and gets its own specs, tests and evidence. Do not merge any PR under this handoff instruction.
