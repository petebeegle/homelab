# Research: Fix Cilium Gateway CRD

## Decision 1: Complete the selected Gateway API release

**Decision**: Add the standard Gateway API v1.5.1 BackendTLSPolicy CRD to the
existing shared CRD Kustomization.

**Rationale**: Cilium 1.20.0 logs BackendTLSPolicy as a required Gateway API type
and disables its Gateway API control plane when the CRD is absent. The repository
already pins the other Gateway API resources to v1.5.1, and the matching upstream
resource URL returns HTTP 200. Cilium's Gateway API documentation lists
BackendTLSPolicy among the CRDs that must be preinstalled:
https://docs.cilium.io/en/latest/network/servicemesh/gateway-api/gateway-api/

**Alternatives considered**:

- Roll back Cilium to 1.19.4: rejected because completing the documented 1.20.0
  prerequisite is smaller and preserves the intended dependency upgrade.
- Install the CRD manually only in production: rejected because it violates
  GitOps and would leave development/bootstrap paths broken.
- Disable Gateway API: rejected because it is the binding ingress contract.

## Decision 2: Preserve the existing mixed channel selection

**Decision**: Add only the standard BackendTLSPolicy manifest and retain the
experimental TLSRoute manifest already selected by the repository.

**Rationale**: The missing required type is independently published in the
standard channel. Existing TLSRoute objects require the experimental CRD shape,
and Cilium's upgrade guidance warns operators using pre-1.20 TLSRoute resources
to retain an experimental definition that includes the older served version.

**Alternatives considered**:

- Replace all Gateway API manifests with the standard bundle: rejected because
  it broadens the incident repair and could make stored TLSRoute objects
  unreadable.
- Upgrade Gateway API beyond v1.5.1: rejected because no version change is
  needed to obtain the required type.

## Decision 3: Validate controller restart behavior in development

**Decision**: Reconcile the shared development base sequentially and observe
whether the operator discovers the new CRD; if not, restart the development
Cilium Operator before repeating the user-path smoke.

**Rationale**: The operator's prerequisite check runs during startup, and the
production process has already completed startup without registering Gateway
secret synchronization. Installing the CRD alone may therefore require an
operator restart, while Envoy should receive certificates dynamically once
secret sync resumes.

**Alternatives considered**:

- Restart all Cilium agents and Envoy pods: rejected because evidence points to
  an operator control-plane discovery failure, not an unhealthy data-plane
  process.
- Trust Gateway status after reconciliation: rejected because current status is
  stale and remained `Programmed=True` during the outage.

## Pre-Implementation Findings

- Production Cilium upgraded to 1.20.0 at 2026-08-01 18:45 UTC.
- Cilium Operator logs name the missing BackendTLSPolicy CRD explicitly.
- Production `cilium-secrets` is empty and Envoy reports zero certificates.
- Every internal HTTPS smoke check resets during TLS negotiation.
- Proxmox telemetry stopped immediately after the upgrade window; its routed
  OTLP hostname fails the same TLS handshake.
- The development cluster is reachable and also lacks the required CRD.
- Before the source edit, development and production renders contain zero
  BackendTLSPolicy definitions.
