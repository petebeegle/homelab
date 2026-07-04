# Feature Specification: immich-dashboard-stats

**Feature Branch**: `codex/immich-dashboard-stats`
**Created**: 2026-07-04
**Status**: Draft
**Risk Tier**: medium
**Input**: User description: "modify the Immich Grafana dashboard with user-oriented stats"

## Summary

Operators need the GitOps-managed `Immich Overview` dashboard to reflect
visible Immich activity during photo uploads and processing. The dashboard must
show library growth, active background queues, job outcomes, processing/storage
latency, users, resource pressure, and relevant warnings instead of mostly
generic health panels that stay flat while Immich is working.

## Binding Sources

- `AGENTS.md`
- `docs/runbooks/spec-driven-development.md`
- `docs/runbooks/implementation-workflow.md`
- `docs/runbooks/immich.md`
- `docs/decisions/codex-implementation-workflow.md`
- `docs/decisions/tdd-and-development-smoke-evidence.md`

## Scope

### In Scope

- Add the minimum Kubernetes desired state needed for Alloy to scrape Immich
  microservices metrics on port `8082`.
- Replace the Immich Grafana dashboard panels with user-oriented Prometheus and
  Loki queries.
- Record live query smoke, render checks, generated architecture status, and
  post-merge verification expectations.

### Out Of Scope

- Grafana alert rules.
- Global Alloy ServiceMonitor support or global scrape-discovery redesign.
- Immich app behavior, external route behavior, secrets, storage classes, or
  user-facing application configuration.

## User Scenarios & Testing

### User Story 1 - See Upload Activity (Priority: P1)

An operator uploading photos can open `Immich Overview` and see asset creation,
background queue activity, and job outcomes move while Immich processes the
library.

**Why this priority**: This addresses the observed failure: uploads and
processing were active, but the dashboard did not reflect useful work.

**Independent Test**: Query-smoke the dashboard PromQL expressions against
production Mimir and validate the Grafana dashboard JSON.

**Acceptance Scenarios**:

1. **Given** Immich metrics are being scraped, **When** assets are uploaded,
   **Then** dashboard panels show non-flat library growth, queue, job, or
   processing metrics.
2. **Given** background work runs in Immich microservices, **When** Alloy
   scrapes the app, **Then** the `metrics-ms` endpoint is available as a
   distinct scrape target.

### User Story 2 - Avoid Misleading Health (Priority: P2)

An operator can trust the scrape-health panel because it evaluates the Immich
API and microservices scrape targets instead of unrelated CNPG service targets.

**Why this priority**: The previous `min(up{namespace="immich"})` query reported
red because of unrelated down PostgreSQL services, even when Immich was working.

**Independent Test**: Smoke the health PromQL query and render the app
manifests that add the microservices metrics service.

**Acceptance Scenarios**:

1. **Given** Immich app metrics targets exist, **When** the dashboard evaluates
   scrape health, **Then** it only considers `immich-server` and
   `immich-server-metrics-ms`.

## Requirements

- **FR-001**: The implementation MUST add a GitOps-managed Service named
  `immich-server-metrics-ms` in namespace `immich` for metrics port `8082`.
- **FR-002**: The implementation MUST keep the existing `immich-server` API
  metrics scrape on port `8081`.
- **FR-003**: The implementation MUST update `Immich Overview` with panels for
  users, new assets, active queues, job rates, processing latency, storage
  latency, process resources, and warning/error logs.
- **FR-004**: Dashboard PromQL and LogQL targets MUST use datasource UIDs
  `prometheus` and `loki`.
- **FR-005**: The implementation MUST NOT add Grafana alert rules or change
  global Alloy scrape behavior.
- **FR-006**: Evidence MUST record query smoke, JSON validation, app render,
  branch overlay render, Grafana render, generated architecture status, and
  any unavailable live post-merge verification.

## Risk And Validation Expectations

**Medium**: Include focused render checks for changed Kubernetes and Grafana
manifests. Because development does not necessarily have the production Immich
observability data required for strict dashboard smoke, use production
read-only Mimir/Loki query smoke plus local render validation. Record post-merge
verification for the new microservices scrape target if Flux has not reconciled
the branch during implementation.

## Success Criteria

- **SC-001**: `kubectl kustomize kubernetes/apps/immich` renders the
  `immich-server-metrics-ms` Service.
- **SC-002**: Branch overlay rendering includes the same service transformed
  into the branch namespace.
- **SC-003**: `jq empty` passes for the updated dashboard JSON.
- **SC-004**: Grafana dashboard kustomizations render successfully.
- **SC-005**: Query smoke shows dashboard queries return data or intentional
  zero-valued fallback vectors.
