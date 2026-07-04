# Feature Specification: pretty-discord-alert-triage-cards

**Feature Branch**: `codex/pretty-discord-alert-triage-cards`
**Created**: 2026-07-04
**Status**: Draft
**Risk Tier**: medium
**Input**: User description: "Implement the homelab side of the already-approved plan for pretty Discord alert triage cards."

## Summary

Upgrade the homelab `pretty-discord-alerts` relay to the upstream v1.4.0 release so Grafana Discord notifications can use the approved triage-card formatting, while reducing normal relay logging from debug to info.

## Binding Sources

- `AGENTS.md`
- `.specify/memory/constitution.md`
- `docs/runbooks/spec-driven-development.md`
- `docs/runbooks/implementation-workflow.md`
- `docs/decisions/codex-implementation-workflow.md`
- `docs/decisions/tdd-and-development-smoke-evidence.md`

## Scope

### In Scope

- Update `kubernetes/infra/monitoring/pretty-discord-alerts/deployment.yaml` to deploy `ghcr.io/petebeegle/pretty-discord-alerts:1.4.0`.
- Change the relay `LOG_LEVEL` environment value from `debug` to `info`.
- Record upstream release and image evidence for PR #3, tag `v1.4.0`, the successful tag workflow, and the GHCR image index.
- Record local validation and the required operator-visible Grafana relay test alert gate.

### Out Of Scope

- Upstream `pretty-discord-alerts` application source changes.
- Grafana alert rule, contact point, or notification policy redesign.
- Discord webhook secret changes.
- Production-first live cluster mutation.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Deploy Triage-Card Relay (Priority: P1)

Operators receive Discord alerts through the relay image that contains the approved triage-card formatting.

**Why this priority**: The image tag is the homelab-controlled desired-state change that makes the upstream feature available.

**Independent Test**: Render the app Kustomization with `kubectl kustomize kubernetes/infra/monitoring/pretty-discord-alerts` and verify the Deployment references image tag `1.4.0`.

**Acceptance Scenarios**:

1. **Given** the repository desired state, **When** Flux reconciles the pretty-discord-alerts Deployment, **Then** the relay pod template references `ghcr.io/petebeegle/pretty-discord-alerts:1.4.0`.
2. **Given** a rendered manifest, **When** reviewing the relay container environment, **Then** `LOG_LEVEL` is set to `info`.

### User Story 2 - Prove Operator-Visible Alert Path (Priority: P2)

An operator-visible test alert proves Grafana can send a notification through the relay to Discord without relying on local render checks alone.

**Why this priority**: Discord card formatting and webhook delivery are user-visible behavior that cannot be fully validated by YAML rendering.

**Independent Test**: Trigger one test alert through Grafana/contact point routing to the pretty-discord-alerts relay in development or another approved validation path, then record the Grafana response, relay logs, relay metrics, cleanup, and any limits on Discord UI observation.

**Acceptance Scenarios**:

1. **Given** the relay is deployed in an approved validation path, **When** a Grafana test alert is sent through the relay, **Then** evidence shows Grafana returned success and the relay reported a successful Discord webhook send.
2. **Given** the agent cannot visually inspect the Discord UI from this environment, **When** evidence is recorded, **Then** it honestly states that limitation instead of claiming direct visual confirmation.

## Requirements *(mandatory)*

- **FR-001**: The implementation MUST set the pretty-discord-alerts Deployment image to `ghcr.io/petebeegle/pretty-discord-alerts:1.4.0`.
- **FR-002**: The implementation MUST set relay `LOG_LEVEL` to `info`.
- **FR-003**: Evidence MUST record that upstream PR #3 was merged, tag `v1.4.0` was pushed at commit `8323c6398612e56586ccbce12adcfdc5d9f3fc2d`, tag workflow run `28707784208` succeeded, and GHCR image tag `1.4.0` was verified.
- **FR-004**: Evidence MUST include the GHCR image index digest `sha256:c110a5297666849cddb6979fa016a6a83b920bb544134a5dec74db4318951d8f` and note that `linux/amd64` and `linux/arm64` platforms are available.
- **FR-005**: Evidence MUST record one operator-visible Grafana/relay test alert before verifier approval or merge readiness, including whether direct Discord UI inspection was possible.
- **FR-006**: The implementation MUST preserve GitOps desired-state flow and avoid durable live-cluster-only changes.
- **FR-007**: If development-cluster validation is unavailable, evidence MUST record the exact blocker and substitute checks.

## Risk And Validation Expectations

This is a medium-risk Kubernetes manifest change affecting a live monitoring notification relay. It requires focused render checks, SDD/workflow validation, architecture generation check, and development-cluster validation when credentials/context are available. If development validation is blocked, the branch remains locally validated but not merge-ready until an operator-visible alert is observed.

## Success Criteria *(mandatory)*

- **SC-001**: The rendered pretty-discord-alerts Kustomization contains image `ghcr.io/petebeegle/pretty-discord-alerts:1.4.0`.
- **SC-002**: The rendered pretty-discord-alerts Kustomization contains `LOG_LEVEL=info`.
- **SC-003**: `python3 tools/codex-harness/validate_sdd_context.py --require-evidence` passes after artifacts are populated.
- **SC-004**: `python3 tools/architecture/render.py --check` passes.
- **SC-005**: Evidence clearly distinguishes local validation, live Grafana/relay smoke results, and the lack of direct Discord UI inspection from this environment.

## Assumptions

- Upstream v1.4.0 contains the approved triage-card implementation from PR #3.
- The existing Service, Secret reference, and Grafana routing remain valid and do not need homelab manifest changes for this release.
- `pretty-discord-alerts` is not a PVC-backed workload, so the NFS storage invariant is not directly involved.

## Open Questions

- None for local implementation. Evidence now includes the user-approved temporary production Grafana/relay smoke result and the Discord UI inspection limitation.
