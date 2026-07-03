# Feature Specification: arr-stack-dashboard

**Feature Branch**: `codex/arr-stack-dashboard`
**Created**: 2026-07-03
**Status**: Draft
**Risk Tier**: medium
**Input**: User description: "and the -arr stack?"

## Summary

Operators need a GitOps-managed Grafana dashboard for the private media automation stack without changing private app manifests or adding application API credentials. The dashboard should use existing cluster metrics and logs for `prowlarr`, `qbittorrent`, `radarr`, `sabnzbd`, `sonarr`, and `whisparr`.

## Binding Sources

- `AGENTS.md`
- `.specify/memory/constitution.md`
- `docs/runbooks/implementation-workflow.md`
- `docs/runbooks/spec-driven-development.md`
- `docs/decisions/observability-stack.md`

## Scope

### In Scope

- An `Arr Stack` Grafana folder.
- An `Arr Stack - Overview` dashboard custom resource backed by a generated ConfigMap.
- Dashboard panels using existing `prometheus` and `loki` datasource UIDs.
- Evidence that all panel query families return strict non-empty live data before implementation.

### Out Of Scope

- Private repository app manifests.
- App API keys, exporters, or credentials.
- Grafana alert rules.

## User Scenarios & Testing

### User Story 1 - Inspect Arr Stack Operations (Priority: P1)

An operator can open one dashboard and see whether the media automation workloads are running, ready, routed, using expected resources, and producing logs.

**Why this priority**: It gives immediate operational value using data already present in Mimir and Loki.

**Independent Test**: Render the Grafana dashboard manifests and validate the dashboard JSON.

**Acceptance Scenarios**:

1. **Given** the Grafana dashboards kustomization, **When** it renders, **Then** it includes an arr stack dashboard ConfigMap and `GrafanaDashboard`.
2. **Given** the parent Grafana kustomization, **When** it renders, **Then** it includes the `Arr Stack` folder and dashboard resources.

### User Story 2 - Trust Dashboard Query Coverage (Priority: P2)

An operator can trust the dashboard panels were not guessed because every included query family returned live data before commit.

**Why this priority**: The user explicitly preferred strict non-empty query smoke for dashboard panels.

**Independent Test**: Run strict query smoke against production Mimir and Loki.

**Acceptance Scenarios**:

1. **Given** production Mimir and Loki access, **When** the query smoke matrix runs, **Then** every dashboard query family returns at least one series, stream, or log line.

## Requirements

- **FR-001**: The implementation MUST add an `Arr Stack` Grafana folder.
- **FR-002**: The implementation MUST add a GitOps-managed Grafana dashboard for `prowlarr`, `qbittorrent`, `radarr`, `sabnzbd`, `sonarr`, and `whisparr`.
- **FR-003**: The dashboard MUST use datasource UID `prometheus` for PromQL panels and `loki` for LogQL panels.
- **FR-004**: Dashboard query targets MUST be limited to expressions whose query family passed strict non-empty smoke before tracked dashboard edits.
- **FR-005**: The implementation MUST NOT add app credentials, exporters, private repo changes, or secret manifests.
- **FR-006**: Evidence MUST record workflow validation, query smoke, JSON validation, render validation, and generated architecture status.

## Risk And Validation Expectations

**Medium**: Include focused render validation for Grafana Operator manifests and live query smoke because this changes Kubernetes-desired Grafana state.

## Success Criteria

- **SC-001**: `jq empty kubernetes/infra/monitoring/grafana/dashboards/arr-stack-dashboard.json` passes.
- **SC-002**: `kubectl kustomize kubernetes/infra/monitoring/grafana/dashboards` passes and renders the arr stack dashboard objects.
- **SC-003**: `kubectl kustomize kubernetes/infra/monitoring/grafana` passes and renders the arr stack folder.
- **SC-004**: Query smoke evidence shows every dashboard query family returned non-empty live data.
- **SC-005**: `python3 tools/architecture/render.py --check` passes or generated architecture is updated.

## Assumptions

- The v1 stack namespace set is `prowlarr`, `qbittorrent`, `radarr`, `sabnzbd`, `sonarr`, and `whisparr`.
- App-specific queue/library health via application APIs remains future work.
- Development cluster validation is substituted by production read-only query smoke plus local render checks.

## Open Questions

- None
