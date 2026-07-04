# Feature Specification: fix-immich-cnpg-scrape

**Feature Branch**: `codex/fix-immich-cnpg-scrape`
**Created**: 2026-07-04
**Status**: Draft
**Risk Tier**: high
**Input**: User description: "ive got an alloy scrape error alert"

## Summary

Stop Alloy from scraping CloudNativePG-generated PostgreSQL Services that do not
expose metrics, while preserving the working pod-level PostgreSQL metrics
scrape.

## Binding Sources

- `AGENTS.md`
- `.specify/memory/constitution.md`
- `docs/runbooks/implementation-workflow.md`
- `docs/runbooks/spec-driven-development.md`
- `docs/runbooks/observability-scrape-topology.md`
- `docs/decisions/observability-stack.md`

## Scope

### In Scope

- Drop CloudNativePG-generated Services from Alloy service metrics discovery.
- Keep pod-level metrics discovery for the CloudNativePG PostgreSQL instance.
- Record live read-only alert triage evidence and local render checks.

### Out Of Scope

- Changing the shared Alloy scrape topology.
- Changing Immich application routing, storage, or authentication.
- Mutating production resources outside Flux-managed desired state.

## User Scenarios & Testing

### User Story 1 - Clear Duplicate Postgres Service Targets (Priority: P1)

Operators need Alloy scrape alerts to identify real scrape failures, not
CloudNativePG service objects that do not expose the annotated metrics port.

**Why this priority**: This directly addresses the active alert.

**Independent Test**: Render the Immich manifests and confirm the CloudNativePG
Cluster no longer applies Prometheus annotations through inherited metadata.

**Acceptance Scenarios**:

1. **Given** CloudNativePG generates PostgreSQL Services, **When** Alloy
   evaluates service metrics discovery, **Then** services labeled with a
   CloudNativePG cluster are dropped from service scraping.

### User Story 2 - Preserve PostgreSQL Pod Metrics (Priority: P2)

Operators still need Immich PostgreSQL metrics available through Alloy.

**Why this priority**: Removing duplicate service targets must not remove useful
database telemetry.

**Independent Test**: Live read-only production query shows the PostgreSQL pod
target is currently up on `:9187`, and local review confirms the pod exposes the
metrics container port.

**Acceptance Scenarios**:

1. **Given** the Immich PostgreSQL pod exposes port `9187`, **When** Alloy
   scrapes pod targets, **Then** the PostgreSQL pod scrape remains available.

## Requirements

- **FR-001**: The implementation MUST drop CloudNativePG-generated Services
  from Alloy service metrics discovery.
- **FR-002**: The implementation MUST preserve GitOps as the source of truth and
  avoid durable live-cluster mutations.
- **FR-003**: The implementation MUST preserve CloudNativePG pod metrics
  scraping for PostgreSQL pods that expose port `9187`.
- **FR-004**: Evidence MUST include the live read-only alert query result, local
  render validation, and any development validation exception.

## Risk And Validation Expectations

**High**: Include focused render checks and live read-only production
verification because the change touches shared Alloy discovery behavior.
Development validation is not representative because the active alert is from
the production monitoring stack and development does not run that stack by
default; record the exception and substitute checks.

## Success Criteria

- **SC-001**: Rendered Alloy config includes a service discovery drop rule for
  services with CloudNativePG cluster labels.
- **SC-002**: Production read-only query identifies only the known Immich
  PostgreSQL service targets as the active Alloy scrape failures before the fix.
- **SC-003**: Local validation commands complete successfully.

## Assumptions

- CloudNativePG `inheritedMetadata` is applied to generated Services and pods,
  which is why the service targets exist even though only the pod exposes the
  metrics port.
- Pod-level Alloy discovery remains sufficient for Immich PostgreSQL metrics.

## Open Questions

- None.
