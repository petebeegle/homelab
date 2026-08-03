# Feature Specification: Fix Cilium Gateway CRD

**Feature Branch**: `codex/fix-cilium-gateway-crd`
**Created**: 2026-08-03
**Status**: Approved
**Risk Tier**: high
**Input**: User description: "Fix the active cluster alerts caused by the Cilium Gateway API outage."

## Human Gate Status

**Intent Brief**: Restore HTTPS routing and dependent Proxmox telemetry after the
Cilium 1.20.0 upgrade, preserve GitOps as the source of truth, avoid changing
alert thresholds or application routes, and verify the exact routed user path.

**Clarify Status**: Skipped because the preceding live investigation identified
one missing required Gateway API type and the user explicitly approved the
proposed forward repair by requesting "fix".

**Spec Gate**: Approved by the user in the incident follow-up after reviewing the
diagnosis and proposed repair sequence.

## Summary

Restore operator-managed HTTPS routing so homelab services and the routed
telemetry endpoint can complete TLS handshakes after the networking controller
upgrade. The repair must make the controller's required API surface part of the
repository's durable desired state and leave existing routes, certificates,
alerts, and application workloads unchanged.

## Binding Sources

- `AGENTS.md`
- `.specify/memory/constitution.md`
- `docs/runbooks/implementation-workflow.md`
- `docs/decisions/flux-gitops-source-of-truth.md`
- `docs/decisions/cilium-gateway-api-ingress.md`
- `docs/decisions/tdd-and-development-smoke-evidence.md`
- `docs/runbooks/development-cluster.md`

## Scope

### In Scope

- Add the required Gateway API type to the shared cluster API definitions.
- Validate that both cluster entrypoints render the required type.
- Validate the shared development base sequentially before production recovery.
- Verify that HTTPS routes complete TLS and dependent telemetry resumes.

### Out Of Scope

- Changes to alert thresholds, notification routing, application routes, or
  certificates.
- Proxmox host maintenance or unrelated node scheduling state.
- Gateway API version changes beyond completing the already selected release's
  required resource set.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Restore routed services (Priority: P1)

As a homelab user, I can open services on the internal HTTPS gateway without the
connection being reset during TLS negotiation.

**Why this priority**: The shared gateway currently blocks every routed service
and is the direct cause of the user-facing outage.

**Independent Test**: Request the lightweight whoami HTTPS endpoint through the
development gateway after the shared base reconciles, then request the
production whoami endpoint after deployment.

**Acceptance Scenarios**:

1. **Given** the networking controller is enabled, **When** its required API
   resources reconcile, **Then** the gateway's certificate material becomes
   available to the data plane.
2. **Given** a valid routed service and hostname, **When** a client negotiates
   HTTPS, **Then** the request receives an HTTP response instead of a TLS reset.

### User Story 2 - Restore dependent telemetry (Priority: P2)

As an operator, I receive current infrastructure telemetry through the routed
collector endpoint so missing-data alerts resolve without suppressing them.

**Why this priority**: Three active alerts are downstream symptoms of the same
routing failure and currently obscure actual infrastructure health.

**Independent Test**: Confirm the routed telemetry endpoint completes TLS and
that infrastructure metric series receive new samples after recovery.

**Acceptance Scenarios**:

1. **Given** the telemetry sender targets the routed collector, **When** HTTPS
   routing recovers, **Then** new infrastructure samples arrive without changing
   alert expressions.

## Requirements *(mandatory)*

- **FR-001**: Shared cluster API definitions MUST include every required Gateway
  API type for the deployed networking controller version.
- **FR-002**: The implementation MUST preserve Git as the durable source of
  cluster state and MUST NOT rely on an unrecorded production-first mutation.
- **FR-003**: Existing Gateway, route, certificate, alert, and application
  definitions MUST remain unchanged.
- **FR-004**: The shared CRD Kustomization MUST render the required API
  definition exactly once, and both cluster entrypoints MUST activate that shared
  Kustomization exactly once.
- **FR-005**: Development validation MUST reconcile the shared base sequentially
  and prove an HTTPS route, or evidence MUST record a genuine unavailable-
  infrastructure exception and substitute checks.
- **FR-006**: Production verification MUST check controller discovery, synced
  certificate material, TLS completion, and current telemetry samples.
- **FR-007**: Evidence MUST distinguish rendered, reconciled, and user-path
  verification layers.

## Risk And Validation Expectations

This is a high-risk cluster-scoped networking and CRD change. Validation must
include broad local rendering, server-side development checks, a sequential
development base reconcile, exact HTTPS smoke, and layered production recovery
checks after the Git change is merged and applied.

## Success Criteria *(mandatory)*

- **SC-001**: The shared CRD Kustomization renders one required Gateway API
  definition, both cluster entrypoints render one activation of the shared CRD
  path, and all three renders complete without Kustomize errors.
- **SC-002**: Development base reconciliation completes and the whoami HTTPS
  endpoint returns a non-5xx HTTP response without a TLS reset.
- **SC-003**: Production Envoy reports at least one configured TLS certificate
  and the whoami and telemetry hostnames complete TLS negotiation.
- **SC-004**: New infrastructure telemetry appears within two normal collection
  intervals after routed ingestion recovers.
- **SC-005**: All synthetic and telemetry alerts caused by this outage resolve
  naturally without alert-rule changes.

## Assumptions

- The already selected Gateway API release contains the missing required type.
- Existing wildcard certificates are valid; the incident investigation showed
  them Ready before implementation.
- The networking operator must restart after API installation to perform its
  startup-time discovery and resume gateway secret synchronization.
- A one-time operator restart after GitOps reconciliation is operational recovery,
  while the API definition remains durable in Git.

## Open Questions

- None.
