# Feature Specification: access-broker-foundation

**Feature Branch**: `codex/access-broker-foundation`
**Created**: 2026-07-04
**Status**: Draft
**Risk Tier**: high
**Input**: User description: "implement the long-term Discord/Auth/VPN broker plan using https://github.com/petebeegle/homelab-access"

## Summary

Create the foundation for a Discord-driven homelab access broker. The broker
application source lives in `petebeegle/homelab-access`; this repository owns
the GitOps deployment contract and safe activation path.

## Binding Sources

- `AGENTS.md`
- `.specify/memory/constitution.md`
- `docs/runbooks/implementation-workflow.md`
- `docs/runbooks/spec-driven-development.md`
- `docs/runbooks/add-secret.md`
- `docs/decisions/flux-gitops-source-of-truth.md`
- `docs/decisions/cilium-gateway-api-ingress.md`
- `docs/decisions/sops-age-secrets.md`
- `docs/decisions/synology-nfs-storage.md`
- `docs/decisions/tdd-and-development-smoke-evidence.md`

## Scope

### In Scope

- Bootstrap `homelab-access` as a Go service with health, readiness, metrics,
  container build, and CI.
- Add an inactive Kubernetes app package for `access-broker` in this repo.
- Define encrypted placeholder secret shape, config, PVC, Deployment, Service,
  and public HTTPRoute contract for future activation.
- Record validation evidence and exceptions.

### Out Of Scope

- Live Discord command handling.
- Authentik user/invite provisioning.
- wg-easy peer provisioning.
- Cloudflare Tunnel activation for `onboard.${cluster_domain}`.
- Production or development Flux activation.

## User Scenarios & Testing

### User Story 1 - App Foundation Exists (Priority: P1)

As an operator, I can review and build a minimal `homelab-access` service before
the access workflow integrations are added.

**Why this priority**: The broker needs a stable app/image contract before this
repo can safely deploy it.

**Independent Test**: Run Go tests in a Go container and build the container
image from the `homelab-access` checkout.

**Acceptance Scenarios**:

1. **Given** the app repo scaffold, **When** tests run, **Then** health,
   readiness, and metrics handlers pass.
2. **Given** the app repo scaffold, **When** the container builds, **Then** a
   runnable image is produced.

### User Story 2 - GitOps Deployment Contract Exists (Priority: P2)

As an operator, I can render the future `access-broker` Kubernetes package
without activating it in a cluster.

**Why this priority**: Deployment shape, secret names, storage, and route shape
can be reviewed before real credentials or public exposure exist.

**Independent Test**: Run `kubectl kustomize kubernetes/apps/access-broker`.

**Acceptance Scenarios**:

1. **Given** the homelab repo desired state, **When** the access-broker package
   is rendered, **Then** it contains a Deployment, Service, PVC, encrypted
   Secret, and Gateway API HTTPRoute.

## Requirements

- **FR-001**: The app repository MUST contain a Go service scaffold with
  `/healthz`, `/readyz`, `/metrics`, `/discord/interactions`, and
  `/download/{token}` endpoints.
- **FR-002**: The app repository MUST include container build and GitHub Actions
  CI definitions.
- **FR-003**: The homelab repository MUST add an inactive `access-broker`
  Kubernetes app package.
- **FR-004**: The package MUST use Gateway API `HTTPRoute` and MUST NOT add
  Kubernetes `Ingress`.
- **FR-005**: The package MUST use StorageClass `nfs-csi-storage` for broker
  persistence.
- **FR-006**: Secret material shape MUST be committed only in SOPS-encrypted
  `secret.yaml`.
- **FR-007**: Evidence MUST record app repo checks, homelab render checks,
  workflow exceptions, and activation deferrals.

## Risk And Validation Expectations

This is high risk because it establishes authentication, VPN, secret, public
route, and future operational automation surfaces. This foundation does not
activate the service, so live development smoke is deferred; local app tests,
container build, render checks, SOPS checks, and architecture check are required.

## Success Criteria

- **SC-001**: `docker run --rm -v "$PWD":/src -w /src golang:1.23-alpine go test ./...`
  passes in the `homelab-access` checkout.
- **SC-002**: `docker build -t homelab-access:foundation .` passes in the
  `homelab-access` checkout.
- **SC-003**: `kubectl kustomize kubernetes/apps/access-broker` passes in this
  repo.
- **SC-004**: The `access-broker` app is not included in production or
  development Flux Kustomization activation lists.

## Assumptions

- `homelab-access` owns application source and image publishing.
- This repo owns deployment manifests, SOPS secrets, routing, Flux activation,
  and operational documentation.
- Runtime provisioning behavior lands in follow-up PRs.

## Open Questions

- None
