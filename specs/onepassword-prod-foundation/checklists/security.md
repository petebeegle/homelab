# Security Requirements Checklist: 1Password Production Foundation

**Purpose**: Validate credential isolation, no-output handling, and safe production behavior
**Created**: 2026-08-09

- [x] CHK001 Is the production token kept out of Git, state, Helm values, arguments, logs, and evidence? [Spec FR-003]
- [x] CHK002 Is the production service account read-only and restricted to `cluster production`? [Spec FR-004]
- [x] CHK003 Does dual bootstrap preserve `sops-age` for rollback? [Spec FR-005]
- [x] CHK004 Do metrics export only item metadata/readiness and never item or Secret data? [Spec FR-006]
- [x] CHK005 Does validation avoid Kubernetes Secret reads and report metadata only? [Spec FR-009]
- [x] CHK006 Is a missing operator detected instead of collapsed to healthy zero? [Spec Edge Cases]
- [x] CHK007 Is automatic deletion limited to the disposable canary namespace? [Spec Edge Cases]
- [x] CHK008 Are existing production consumers explicitly excluded from this phase? [Spec FR-005]
- [x] CHK009 Are unavailable credentials or cluster access blocking conditions rather than exceptions? [Spec FR-011]
- [x] CHK010 Is Connect excluded by configuration and render assertion? [Spec FR-001]
