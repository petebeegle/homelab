# Registry Plan Requirements Checklist

**Audience**: Implementer and PR reviewer. **Depth**: High risk, scoped to registry authorization, routing, state and rollout. **Date**: 2026-10-03.

- [x] CHK001 Are hosted and group endpoints and their separate purposes explicit? [Clarity; Spec FR-001/004/005; Plan Global Constraints]
- [x] CHK002 Are publisher permissions enumerated and consumer/anonymous write denials defined? [Coverage; Spec FR-002/003; Contract acceptance matrix]
- [x] CHK003 Are credential and state confidentiality requirements specified for outputs, logs and smoke files? [Completeness; Plan Technical Context]
- [x] CHK004 Does the plan address missing state and random-password import replacement without allowing silent rotation? [Recovery; Plan state recovery]
- [x] CHK005 Is the unresolved credential recovery decision explicitly a production prerequisite, rather than a silently approved reset? [Consistency; Spec assumptions; Plan Human Gates]
- [x] CHK006 Are mutable-tag and old-digest behaviors both specified? [Clarity; Spec FR-008; Contract acceptance matrix]
- [x] CHK007 Are realm/upload URL, TLS and private-network requirements measurable? [Measurability; Spec FR-005/007; Plan private HTTPS path]
- [x] CHK008 Does validation require actual multi-layer push and an independent pull? [Acceptance quality; Spec FR-010; Contract]
- [x] CHK009 Are existing group/upstream pulls and preserved NAS data explicit regression requirements? [Coverage; Spec FR-004/006/012]
- [x] CHK010 Does the development design name isolated context/state/credentials and explain cleanup and storage? [Completeness; Plan Development fixture]
- [x] CHK011 Are the limits of readiness probes and development topology acknowledged? [Consistency; Plan validation; Research]
- [x] CHK012 Are deployment ordering, container restart impact and non-destructive rollback specified? [Recovery; Plan NAS connector and risks]
- [x] CHK013 Does the plan preserve exact Gateways and avoid new public exposure, PRO features or an unintended image upgrade? [Constraints; Plan Global Constraints]
- [x] CHK014 Are plan approval, task/analysis approval and credential recovery distinguished from completed implementation? [Clarity; Plan Human Gates]

The checklist validates the written requirements and plan. It does not assert that the implementation or deployment passes these checks. The current consumer secret/state recovery remains operationally unresolved.
