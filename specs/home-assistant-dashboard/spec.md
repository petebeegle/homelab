# Feature Specification: home-assistant-dashboard

**Feature Branch**: `codex/home-assistant-dashboard`
**Created**: 2026-07-03
**Status**: Draft
**Risk Tier**: medium
**Input**: User description: "Create a Home Assistant Grafana dashboard using only query-smoked existing Prometheus and Loki data."

## Summary

Operators need a GitOps-managed Grafana dashboard that summarizes Home Assistant health, routing, resource use, recent logs, observed integration activity, and synthetic smoke status without adding Home Assistant API credentials or new exporters.

## Binding Sources

- `AGENTS.md`
- `.specify/memory/constitution.md`
- `docs/runbooks/implementation-workflow.md`
- `docs/runbooks/spec-driven-development.md`
- `docs/decisions/observability-stack.md`
- `docs/runbooks/home-assistant.md`

## Scope

### In Scope

- A Home Assistant Grafana folder.
- A Home Assistant dashboard custom resource backed by a generated ConfigMap.
- Dashboard panels using existing `prometheus` and `loki` datasource UIDs.
- Evidence that all panel queries return strict non-empty live data before implementation.

### Out Of Scope

- Home Assistant Prometheus integration.
- Home Assistant API credentials or live integration inventory.
- Grafana alert rules.

## User Scenarios & Testing

### User Story 1 - Inspect Home Assistant Operations (Priority: P1)

An operator can open one dashboard and see whether Home Assistant is running, ready, routed, using expected resources, and producing logs.

**Why this priority**: This is the smallest useful dashboard slice and uses only existing observability data.

**Independent Test**: Render the Grafana dashboard manifests and validate the JSON.

**Acceptance Scenarios**:

1. **Given** the Grafana dashboards kustomization, **When** it renders, **Then** it includes a Home Assistant dashboard ConfigMap and `GrafanaDashboard`.
2. **Given** the dashboard JSON, **When** it is parsed with `jq`, **Then** it is valid JSON with datasource UIDs `prometheus` and `loki`.

### User Story 2 - Trust Dashboard Query Coverage (Priority: P2)

An operator can trust that v1 panels were not guessed because every included query returned live data before the dashboard was committed.

**Why this priority**: Empty panels reduce dashboard confidence and were explicitly rejected by the user.

**Independent Test**: Run strict query smoke against production Mimir and Loki.

**Acceptance Scenarios**:

1. **Given** production Mimir and Loki access, **When** the query smoke matrix runs, **Then** every dashboard query returns at least one series, stream, or log line.

## Requirements

- **FR-001**: The implementation MUST add a Home Assistant Grafana folder.
- **FR-002**: The implementation MUST add a GitOps-managed Grafana dashboard for Home Assistant.
- **FR-003**: The dashboard MUST use datasource UID `prometheus` for PromQL panels and `loki` for LogQL panels.
- **FR-004**: Dashboard query targets MUST be limited to expressions that passed strict non-empty smoke before tracked dashboard edits.
- **FR-005**: The implementation MUST NOT add Home Assistant API credentials, Home Assistant Prometheus integration, or secret manifests.
- **FR-006**: Evidence MUST record workflow validation, query smoke, JSON validation, render validation, and generated architecture status.

## Risk And Validation Expectations

**Medium**: Include focused render validation for Grafana Operator manifests and live query smoke because this changes Kubernetes-desired Grafana state.

## Success Criteria

- **SC-001**: `jq empty kubernetes/infra/monitoring/grafana/dashboards/home-assistant-dashboard.json` passes.
- **SC-002**: `kubectl kustomize kubernetes/infra/monitoring/grafana/dashboards` passes and renders the Home Assistant dashboard objects.
- **SC-003**: Query smoke evidence shows every dashboard query returned non-empty live data.
- **SC-004**: `python3 tools/architecture/render.py --check` passes or generated architecture is updated.

## Assumptions

- Runtime Home Assistant integration inventory remains future work unless a dedicated exporter or authenticated API path is designed.
- Observed integration activity from logs is acceptable for v1.
- Development Grafana validation is substituted by production read-only query smoke plus local render checks.

## Open Questions

- None
