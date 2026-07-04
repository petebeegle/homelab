# Feature Specification: immich-app

**Feature Branch**: `codex/immich-app`
**Created**: 2026-07-04
**Status**: Draft
**Risk Tier**: high
**Input**: User description: "lets deploy immich to the homelab. we'll add it as an app, add dashboards from exposed prometheus metrics, back it by the NAS, and add it to homepage"

## Summary

Deploy Immich as a GitOps-managed homelab photo app, reachable on the LAN and
WireGuard service plane, with photo assets stored on the Synology-backed media
StorageClass, PostgreSQL stored on node-local Kubernetes storage, Authentik/OIDC
as the only production login path, Grafana dashboards from Prometheus metrics,
and a Homepage launch tile.

## Binding Sources

- `AGENTS.md`
- `.specify/memory/constitution.md`
- `docs/runbooks/spec-driven-development.md`
- `docs/runbooks/implementation-workflow.md`
- `docs/runbooks/add-app.md`
- `docs/runbooks/development-cluster.md`
- `docs/decisions/flux-gitops-source-of-truth.md`
- `docs/decisions/cilium-gateway-api-ingress.md`
- `docs/decisions/sops-age-secrets.md`
- `docs/decisions/synology-nfs-storage.md`
- `docs/decisions/observability-stack.md`
- `docs/decisions/talos-management-boundaries.md`

## Scope

### In Scope

- Add reusable local-path storage for database PVCs.
- Add CloudNativePG and an Immich PostgreSQL cluster with VectorChord support.
- Add the Immich Kubernetes app, NAS media PVC, Gateway route, and Flux wiring.
- Add Authentik OAuth/OIDC blueprint and SOPS-encrypted Immich secrets.
- Add Grafana dashboard resources for Immich metrics.
- Add Homepage and synthetic smoke coverage for Immich.
- Update generated architecture and durable runbook/spec evidence.

### Out Of Scope

- Internet-public Cloudflare Tunnel exposure.
- Importing an existing photo library.
- NAS-hosted PostgreSQL outside Kubernetes.
- Production user/group membership changes outside declarative Authentik setup.
- Full database backup automation beyond Immich automatic backups and documented
  follow-up.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Store Photos In Immich (Priority: P1)

Operators need Immich deployed as a routable app with photo/video assets stored
on the NAS media storage class.

**Why this priority**: This is the core user-facing capability and proves the
app, route, storage, and GitOps wiring.

**Independent Test**: Render and development-smoke the Immich app, then verify
the production route and app health after Flux reconciliation.

**Acceptance Scenarios**:

1. **Given** the production app manifests, **When** Flux applies the branch,
   **Then** Immich serves `https://immich.${cluster_domain}` through the internal
   and external service-plane Gateways and uses a 1 TiB
   `nfs-csi-media-storage` library PVC.

### User Story 2 - Keep Database Off NFS (Priority: P1)

Operators need Immich metadata stored in PostgreSQL without placing the database
data directory on a NAS network share.

**Why this priority**: Immich database state is required to recover the library
metadata, and upstream warns against network-share database storage.

**Independent Test**: Render infra and app manifests and verify the Immich
PostgreSQL PVC uses `local-path`, not an NFS StorageClass.

**Acceptance Scenarios**:

1. **Given** the database manifests, **When** they are rendered, **Then** the
   CloudNativePG cluster uses VectorChord-capable PostgreSQL and a local-path
   PVC.

### User Story 3 - Sign In Through Authentik (Priority: P1)

Operators need Immich protected by Authentik/OIDC with no native Immich password
login in production.

**Why this priority**: The app contains private photos and must follow the
homelab SSO pattern requested by the user.

**Independent Test**: Render the Authentik blueprint and Immich config secret
references, then verify the live route redirects to or offers Authentik OAuth.

**Acceptance Scenarios**:

1. **Given** the Authentik and Immich config, **When** a user opens Immich,
   **Then** OAuth is enabled, native password login is disabled, and mobile/web
   redirect URIs are registered.

### User Story 4 - Observe Immich (Priority: P2)

Operators need Grafana panels fed by Immich Prometheus metrics and Homepage
navigation to the app.

**Why this priority**: It completes the operational expectations without
blocking the initial app deployment.

**Independent Test**: Render Grafana and Homepage resources, then verify live
Grafana dashboard data and the Homepage tile after reconciliation.

**Acceptance Scenarios**:

1. **Given** Immich metrics are enabled, **When** Alloy scrapes the service,
   **Then** Grafana shows Immich health, request, resource, database, and log
   panels.

## Requirements *(mandatory)*

- **FR-001**: The implementation MUST deploy Immich from the official OCI Helm
  chart with a pinned chart version and pinned Immich image tag.
- **FR-002**: The implementation MUST store Immich library assets on a 1 TiB
  `nfs-csi-media-storage` PVC.
- **FR-003**: The implementation MUST keep Immich PostgreSQL data on a
  non-default local StorageClass and not on NFS.
- **FR-004**: The implementation MUST deploy PostgreSQL through CloudNativePG
  using a VectorChord-capable image and initialize the `vchord` extension.
- **FR-005**: The implementation MUST expose Immich only through Gateway API
  `HTTPRoute` parents `gateway/internal` and `gateway/external`.
- **FR-006**: The implementation MUST configure Authentik OAuth for Immich,
  including mobile and web redirect URIs, and disable native password login in
  production Immich configuration.
- **FR-007**: The implementation MUST commit only SOPS-encrypted secret
  manifests.
- **FR-008**: The implementation MUST enable Immich Prometheus metrics and add a
  Grafana dashboard managed by Grafana Operator resources.
- **FR-009**: The implementation MUST add Immich to Homepage and production
  synthetic route smoke coverage.
- **FR-010**: Evidence MUST record local render checks, Terraform validation,
  secret encryption checks, development validation or a precise exception, and
  any unavailable live-cluster verification.

## Risk And Validation Expectations

**High**: This implementation adds storage infrastructure, a database operator,
a database-backed app, SOPS secrets, Gateway routes, Authentik login behavior,
dashboards, and Homepage/synthetic app coverage. Use broad local validation,
development base reconciliation with `--include-cluster-base` where available,
and exact production path verification after merge.

## Success Criteria *(mandatory)*

- **SC-001**: Production and development cluster kustomizations render
  successfully.
- **SC-002**: Rendered Immich manifests include a 1 TiB
  `nfs-csi-media-storage` library PVC and a local-path PostgreSQL PVC.
- **SC-003**: Rendered Immich route attaches to internal and external Gateway
  HTTPS listeners and no public Gateway.
- **SC-004**: Rendered secrets are SOPS encrypted with no plaintext
  `stringData`/`data`.
- **SC-005**: Grafana dashboard and Homepage config render with Immich entries.
- **SC-006**: Development validation is run or a concrete unavailable
  infrastructure/credentials exception is recorded with substitute checks.

## Assumptions

- Immich chart `0.13.1` and app image `v3.0.1` are the intended initial pins.
- CloudNativePG uses `tensorchord/cloudnative-vectorchord:16.14-1.1.1`.
- Valkey may use the Immich chart's embedded `emptyDir` cache for v1.
- Development validation cannot fully prove Authentik because the development
  cluster intentionally omits Authentik.

## Open Questions

- None.
