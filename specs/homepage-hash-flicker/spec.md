# Feature Specification: Homepage Hash Flicker

**Feature Branch**: `codex/homepage-hash-flicker`
**Created**: 2026-07-04
**Status**: Draft
**Risk Tier**: medium
**Input**: User description: "Fix Homepage first-load reload/flicker caused by alternating `/api/hash` responses behind the Service."

## Summary

Homepage should load without repeated browser reloads or flicker. Read-only live
checks showed the dashboard HTML returns `200` without redirects, but
`/api/hash` alternates between two values while Homepage runs with two replicas.
Homepage reloads when that hash changes, so the shared Deployment should use one
replica until a future design can make the hash stable across pods.

## Binding Sources

- `AGENTS.md`
- `.specify/memory/constitution.md`
- `docs/runbooks/spec-driven-development.md`
- `docs/runbooks/implementation-workflow.md`
- `docs/runbooks/development-cluster.md`
- `docs/decisions/cilium-gateway-api-ingress.md`
- `docs/decisions/flux-gitops-source-of-truth.md`

## Scope

### In Scope

- Change the shared Homepage Deployment replica count from two to one.
- Preserve the existing Service, HTTPRoute, PDB, config merge flow, and branch
  Homepage manifest.
- Record the availability tradeoff and validation evidence.

### Out Of Scope

- Redesigning Homepage config hashing or the config reloader.
- Adding session affinity, shared persistent config state, or new Gateway
  routing behavior.
- Changing private Homepage configuration.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Stable Homepage Load (Priority: P1)

As a dashboard user, I can open Homepage without the page repeatedly reloading
because backend hash responses disagree.

**Why this priority**: This directly fixes the reported user-facing flicker with
the smallest GitOps change.

**Independent Test**: Render the production and development Homepage manifests
and confirm the shared Deployment renders with `replicas: 1`; after deployment,
curl the exact user URL and repeatedly sample `/api/hash` to confirm only one
hash value is returned.

**Acceptance Scenarios**:

1. **Given** the rendered shared Homepage Deployment, **When** production or
   development kustomizations are rendered, **Then** the Deployment has exactly
   one replica.
2. **Given** the production Homepage URL after Flux applies the change, **When**
   `/api/hash` is requested at least 20 times, **Then** only one unique hash is
   observed.
3. **Given** the production Homepage URL after Flux applies the change, **When**
   the page is loaded in a browser or browser automation, **Then** Homepage does
   not repeatedly reload due to hash churn.

## Requirements *(mandatory)*

- **FR-001**: The shared Homepage Deployment MUST render with `replicas: 1`.
- **FR-002**: The implementation MUST preserve existing Homepage Service,
  HTTPRoute, PDB, config merge, and branch manifest behavior.
- **FR-003**: Evidence MUST record the intentional tradeoff of lower Homepage
  availability for stable browser behavior.
- **FR-004**: Evidence MUST include production and development render checks.
- **FR-005**: Evidence MUST include development validation or a documented
  unavailable-infrastructure exception with substitute checks.

## Risk And Validation Expectations

This is `medium` risk because it changes a Kubernetes app workload. It requires
focused render checks and development validation when credentials are available,
or a documented exception with substitute checks when they are not.

## Success Criteria *(mandatory)*

- **SC-001**: Rendered production Homepage manifests include `replicas: 1` for
  the `homepage/homepage` Deployment.
- **SC-002**: Rendered development Homepage manifests include `replicas: 1` for
  the `homepage/homepage` Deployment.
- **SC-003**: Production Homepage returns `200` with no redirects from the exact
  user URL before or after deployment verification.
- **SC-004**: Post-deployment `/api/hash` sampling returns one unique hash over
  at least 20 requests, or the missing post-deployment layer is explicitly
  recorded for follow-up.

## Assumptions

- The fastest reliable fix is preferred over preserving two-replica Homepage
  availability.
- No secret staging is required.
- `docs/architecture.md` is not expected to change for a replica-count-only app
  workload adjustment unless validation reports it stale.

## Open Questions

- None
