# Feature Specification: home-assistant-dashboard-activity

**Feature Branch**: `codex/home-assistant-dashboard-activity`
**Created**: 2026-07-04
**Status**: Draft
**Risk Tier**: medium
**Input**: User description: "Add native Home Assistant Prometheus activity metrics to the Home Assistant dashboard, replacing synthetic smoke-specific panels while preserving operational health coverage."

## Summary

Operators should be able to inspect Home Assistant activity from native Home
Assistant Prometheus metrics in the existing Grafana dashboard. The dashboard
should retain Kubernetes health, route, PVC, resource, and application log
coverage, while synthetic smoke-specific panels move out of the Home Assistant
overview.

## Binding Sources

- `AGENTS.md`
- `.specify/memory/constitution.md`
- `docs/runbooks/implementation-workflow.md`
- `docs/runbooks/spec-driven-development.md`
- `docs/runbooks/development-cluster.md`
- `docs/decisions/codex-implementation-workflow.md`
- `docs/decisions/tdd-and-development-smoke-evidence.md`
- `docs/decisions/cilium-gateway-api-ingress.md`
- `docs/decisions/sops-age-secrets.md`
- Home Assistant Prometheus integration docs: https://www.home-assistant.io/integrations/prometheus/

## Scope

### In Scope

- Enable the native Home Assistant Prometheus exporter in production and branch
  Home Assistant configuration.
- Annotate production and branch Home Assistant Services for internal
  Prometheus scraping of `/api/prometheus` on port 80.
- Replace synthetic smoke-specific Home Assistant dashboard panels with an
  Activity row backed by Prometheus queries for entity changes, unavailable
  entities, active lights, active switches, active binary sensors, and
  entity/area metadata.
- Preserve dashboard coverage for Home Assistant Kubernetes health, route
  status, PVC phase, CPU, memory, and Home Assistant logs.
- Record workflow, local validation, development validation attempt, live query
  smoke attempt, exceptions, and final branch state.

### Out Of Scope

- New secrets, external routes, internet-public exposure, or bearer token
  management.
- Changing the standalone synthetic smoke dashboard.
- Exact Home Assistant Logbook prose reconstruction; dashboard activity is
  Prometheus-derived.
- Verifier approval artifacts or PR creation.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Native Activity Metrics (Priority: P1)

An operator can open the Home Assistant Grafana dashboard and see recent native
Home Assistant entity activity and current entity state summaries.

**Why this priority**: Native Home Assistant activity is the core user outcome
and replaces lower-signal synthetic smoke-specific panels in this dashboard.

**Independent Test**: `jq empty` validates the dashboard JSON and review of the
dashboard panel titles and Prometheus expressions confirms the Activity row uses
Home Assistant metrics with the `prometheus` datasource.

**Acceptance Scenarios**:

1. **Given** the Home Assistant dashboard JSON, **When** an operator reviews the
   panel list, **Then** it includes an Activity row with Prometheus panels for
   recent entity changes, unavailable entities, active lights, active switches,
   active binary sensors, and entity/area metadata.
2. **Given** the Home Assistant dashboard JSON, **When** an operator reviews
   removed panel titles, **Then** `Smoke Failures`, `Synthetic Smoke`,
   `Synthetic Pod State`, `Smoke Summary Logs`, `Home Assistant Route Smoke
   Logs`, and `Pod Phases` are absent.

### User Story 2 - Scrapeable Home Assistant Exporter (Priority: P2)

Prometheus can discover and scrape the Home Assistant native exporter from both
production and branch app manifests without new credentials.

**Why this priority**: Dashboard panels need native metrics to exist in Mimir,
and branch validation should exercise the same exporter behavior.

**Independent Test**: `kubectl kustomize kubernetes/apps/home-assistant` and
`kubectl kustomize kubernetes/apps/home-assistant/branch` render configuration
with the Prometheus exporter and Service scrape annotations.

**Acceptance Scenarios**:

1. **Given** production Home Assistant rendered manifests, **When** the
   ConfigMap and Service are inspected, **Then** the Prometheus exporter is
   enabled with namespace `homeassistant`, `requires_auth: false`, the approved
   domain filter, and scrape annotations for `/api/prometheus`.
2. **Given** branch Home Assistant rendered manifests, **When** the ConfigMap
   and Service are inspected, **Then** they expose the same exporter behavior
   using branch names and namespaces.

### User Story 3 - Operational Coverage Preserved (Priority: P3)

An operator keeps the existing Home Assistant operational view while activity
metrics are added.

**Why this priority**: The dashboard should become more app-relevant without
losing health, route, storage, resource, or log signals.

**Independent Test**: `kubectl kustomize kubernetes/infra/monitoring/grafana/dashboards`
renders the dashboard ConfigMap and review confirms retained panels remain.

**Acceptance Scenarios**:

1. **Given** the updated dashboard JSON, **When** an operator reviews panel
   titles, **Then** Kubernetes health, route acceptance, route refs, PVC phase,
   CPU, memory, and Home Assistant log panels remain.

## Requirements *(mandatory)*

- **FR-001**: The implementation MUST enable Home Assistant `prometheus:` in
  production and branch configuration with namespace `homeassistant`,
  `requires_auth: false`, and `filter.include_domains` containing `light`,
  `switch`, `binary_sensor`, `sensor`, `person`, `device_tracker`,
  `automation`, `climate`, `cover`, `fan`, `lock`, and `update`.
- **FR-002**: The implementation MUST annotate production and branch Home
  Assistant Services with `prometheus.io/scrape: "true"`,
  `prometheus.io/port: "80"`, and `prometheus.io/path: /api/prometheus`.
- **FR-003**: The dashboard MUST remove panels titled `Smoke Failures`,
  `Synthetic Smoke`, `Synthetic Pod State`, `Smoke Summary Logs`, `Home
  Assistant Route Smoke Logs`, and `Pod Phases`.
- **FR-004**: The dashboard MUST add an `Activity` row with Prometheus panels
  for recent entity changes, currently unavailable entities, active lights,
  active switches, active binary sensors, and entity/area metadata joined
  through `homeassistant_entity_info` where useful.
- **FR-005**: The dashboard MUST preserve Kubernetes health, route, PVC, CPU,
  memory, and Home Assistant log coverage.
- **FR-006**: The implementation MUST keep Grafana datasource UIDs
  `prometheus` and `loki` and MUST NOT add new secrets or external routes.
- **FR-007**: Evidence MUST record required local checks, SDD/workflow
  validators, the development validation attempt or exact exception, the live
  metric query smoke attempt or exact exception, final branch, final `HEAD`, and
  that verifier approval was not created.

## Risk And Validation Expectations

**Medium**: Include local Kubernetes and Grafana render checks plus
development-cluster validation for the Home Assistant branch app when
prerequisites are available. If development infrastructure, credentials, or
cluster access are unavailable, record the exact exception and substitute local
checks. Attempt a live Grafana/Mimir query for new `homeassistant_*` metrics if
credentials are available; otherwise record the exact unauthorized or
unavailable exception.

## Success Criteria *(mandatory)*

- **SC-001**: Production and branch Home Assistant kustomize output includes
  the approved Prometheus exporter configuration and Service annotations.
- **SC-002**: The Home Assistant dashboard JSON is valid JSON and no longer
  contains the removed synthetic smoke-specific panel titles.
- **SC-003**: The Home Assistant dashboard contains an Activity row with
  Prometheus datasource panels based on native Home Assistant metrics.
- **SC-004**: Dashboard kustomize render and architecture check pass, or
  generated architecture is updated if the check reports drift.
- **SC-005**: Evidence and PR summary document all local checks, development
  validation, live metric query smoke, exceptions, final branch state, and
  verifier-approval absence.

## Assumptions

- Internal Service scraping makes `requires_auth: false` acceptable for the
  Home Assistant Prometheus endpoint.
- Prometheus metrics appear only after Home Assistant restarts with the updated
  configuration and Prometheus scrapes `/api/prometheus`.
- Home Assistant's documented `entity_info` metric is prefixed by the configured
  namespace, so this implementation uses `homeassistant_entity_info`.

## Open Questions

- None.
