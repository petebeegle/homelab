# Cutover Requirements Checklist: Production Grafana Credential Cutover

**Purpose**: Validate that the production authentication cutover requirements are complete, bounded, measurable, and recoverable before task generation
**Created**: 2026-08-29
**Feature**: [spec.md](../spec.md)

## Scope And Boundary

- [x] CHK001 Is the single credential family and every included consumer purpose explicitly defined? [Completeness, Spec §Scope/FR-001]
- [x] CHK002 Is the notification webhook credential explicitly excluded and required to remain unchanged? [Clarity, Spec §Out Of Scope/FR-002]
- [x] CHK003 Are all unrelated infrastructure and application consumers explicitly excluded? [Coverage, Spec §Out Of Scope/FR-007]

## Credential Safety

- [x] CHK004 Are value-redaction and exact key/byte parity requirements specified before cutover? [Security, Spec §FR-004]
- [x] CHK005 Is generated-credential readiness defined as a mandatory precondition? [Completeness, Spec §FR-005]
- [x] CHK006 Are legacy credential retention and decryption support requirements consistent with the rollback scenario? [Consistency, Spec §FR-003/US2]
- [x] CHK007 Does the spec prohibit destructive generated-item deletion during rollback? [Recovery, Spec §FR-008]

## Acceptance And Recovery

- [x] CHK008 Are automated availability, rollout, operator, and data-source acceptance requirements distinguished from manual authentication acceptance? [Clarity, Spec §FR-006]
- [x] CHK009 Is the manual user path measurable in URL, login method, dashboard behavior, and completion time? [Measurability, Spec §SC-004]
- [x] CHK010 Are partial-success cases addressed, including healthy anonymous probes with failed OAuth or dashboard management? [Exception Coverage, Spec §US1/FR-006]
- [x] CHK011 Is the rollback boundary limited to Grafana references with observable recovery expectations? [Recovery, Spec §US2/FR-008]
- [x] CHK012 Does required evidence cover reviewed, merged, fetched, applied, live-reference, automated-smoke, manual-smoke, and rollback layers without secret values? [Traceability, Spec §FR-009]

## Environment Assumptions

- [x] CHK013 Is the missing development Grafana environment documented with safe substitute validation rather than treated as silent coverage? [Assumption, Spec §Risk And Validation Expectations]
- [x] CHK014 Is the assumption that existing OAuth registration and credential bytes are already correct explicitly bounded from repair or rotation? [Assumption, Spec §Assumptions]

## Notes

- All requirements-quality items pass. Implementation behavior remains subject to tasks, automated checks, and the user's post-merge manual smoke.
