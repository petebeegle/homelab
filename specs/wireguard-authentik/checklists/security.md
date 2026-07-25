# Security Requirements Checklist: WireGuard Authentik

**Purpose**: Review whether the authentication, authorization, failure, machine
access, rollout, and recovery requirements are complete enough for a high-risk
PR
**Created**: 2026-07-25
**Feature**: [spec.md](../spec.md)

**Note**: This checklist reviews the requirements as written; it is not an
implementation test plan. Depth is standard, and the intended user is a PR
reviewer at the plan gate.

## Authentication And Authorization Completeness

- [x] CHK001 Are authentication requirements defined for every path on the
      protected `vpn` hostname, including representative API paths?
      [Completeness, Spec §FR-001]
- [x] CHK002 Is the authorized population defined more narrowly than "all
      authenticated users," with a stable group and explicit default-deny
      behavior? [Clarity, Spec §FR-002]
- [x] CHK003 Are the authorized-member and authenticated-non-member outcomes
      both specified independently? [Coverage, Spec §User Story 2]
- [x] CHK004 Is the relationship between the Authentik gate and wg-easy's own
      authentication unambiguous for both humans and API clients?
      [Consistency, Spec §FR-006]

## Failure And Recovery Coverage

- [x] CHK005 Is fail-closed behavior defined for Authentik and proxy-component
      unavailability, with direct-to-wg-easy fallback explicitly prohibited?
      [Exception Flow, Spec §FR-003]
- [x] CHK006 Are requirements present for invalid Gateway backend references
      and other partial rollout states? [Coverage, Plan §Risks]
- [x] CHK007 Is recovery access defined without weakening the durable
      user-facing policy or requiring plaintext credentials?
      [Recovery, Spec §Scope]
- [x] CHK008 Is Git-revert rollback distinguished from a temporary live
      diagnostic mutation? [Consistency, Plan §Implementation Steps]

## Boundary And Non-Goal Clarity

- [x] CHK009 Is the protected browser boundary clearly separated from the
      WireGuard UDP data plane and direct in-cluster machine boundary?
      [Clarity, Spec §FR-005]
- [x] CHK010 Are exposure changes to external/public Gateways explicitly
      excluded? [Scope, Spec §Out Of Scope]
- [x] CHK011 Is preservation of peers, persistent database contents, Service
      identity, and access-broker behavior stated in objectively reviewable
      terms? [Measurability, Spec §SC-003]
- [x] CHK012 Are other non-Authentik apps and Valheim explicitly separated from
      the implementation scope while retaining the audit as planning input?
      [Scope, Spec §Out Of Scope]

## Evidence And Acceptance Quality

- [x] CHK013 Can the unauthenticated acceptance requirement be measured at the
      exact root and API paths without exposing secrets?
      [Acceptance Criteria, Spec §SC-001]
- [x] CHK014 Are both authorization personas, Authentik outage, UDP peer
      continuity, and direct API continuity covered by requirements?
      [Scenario Coverage, Spec §User Scenarios]
- [x] CHK015 Is the development-cluster gap documented with a reason,
      substitute evidence, and a rule that real failures cannot be waived?
      [Dependency, Plan §Development Validation]
- [x] CHK016 Does completion require fetched/applied revision evidence and the
      exact user path rather than route readiness alone?
      [Acceptance Criteria, Spec §SC-005]

## Notes

- All 16 requirement-quality checks pass against the current spec and plan.
- Task generation and implementation remain gated on human approval of the
  chosen proxy-mode approach and rollout evidence.
