# Feature Specification: immich-dashboard-inline

**Feature Branch**: `codex/immich-dashboard-inline`
**Created**: 2026-07-04
**Status**: Draft
**Risk Tier**: medium
**Input**: User description: "merged but no change"

## Summary

The merged Immich dashboard update reached Flux and updated the generated
ConfigMap, but Grafana still served the old dashboard. Operators need the
GitOps dashboard content to update Grafana reliably when dashboard JSON changes.

## Binding Sources

- `AGENTS.md`
- `docs/runbooks/spec-driven-development.md`
- `docs/runbooks/implementation-workflow.md`
- `docs/runbooks/immich.md`

## Scope

### In Scope

- Change only the Immich Grafana dashboard resource so dashboard JSON is part of
  `GrafanaDashboard.spec`.
- Remove the now-unused Immich dashboard ConfigMap generator.
- Record the live diagnosis and post-merge Grafana API verification target.

### Out Of Scope

- Other dashboards.
- Grafana Operator upgrades or global dashboard-management redesign.
- Immich app, route, storage, or secret changes.

## User Scenarios & Testing

### User Story 1 - Dashboard Actually Updates (Priority: P1)

An operator who merges an Immich dashboard change sees the new panels in
Grafana, not only in the Kubernetes ConfigMap.

**Why this priority**: The previous PR applied in Flux but did not change the
dashboard visible through Grafana's API/UI.

**Independent Test**: Render Grafana manifests locally and, after merge, query
Grafana API for `uid=immich-overview` to confirm the new panel titles.

**Acceptance Scenarios**:

1. **Given** the Immich dashboard JSON changes, **When** Flux applies the
   dashboard resource, **Then** the `GrafanaDashboard` spec changes and the
   operator imports the new dashboard into Grafana.

## Requirements

- **FR-001**: The Immich `GrafanaDashboard` MUST use inline `spec.json`.
- **FR-002**: The Immich dashboard ConfigMap generator MUST be removed because
  it is no longer consumed.
- **FR-003**: The dashboard UID MUST remain `immich-overview`.
- **FR-004**: Evidence MUST record local render checks and the post-merge
  Grafana API verification expectation.

## Risk And Validation Expectations

**Medium**: Include focused render validation for Grafana Operator manifests and
generated architecture checks. Production Grafana API verification is the
post-merge acceptance check.
