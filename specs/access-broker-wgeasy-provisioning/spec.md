# Feature Specification: access-broker-wgeasy-provisioning

**Feature Branch**: `codex/access-broker-wgeasy-provisioning`
**Date**: 2026-07-17
**SDD Tier**: medium

## Intent Brief

Deploy the merged `homelab-access` WireGuard provisioning support to the
production access-broker so `/access approve` can create or reuse a wg-easy peer
and return a single-use config download link after Authentik user provisioning.

## Scope

- Roll the production access-broker pod so it pulls `ghcr.io/petebeegle/homelab-access:main`
  after homelab-access PR #9.
- Make the wg-easy username configuration explicit in the access-broker
  ConfigMap.
- Preserve existing public Gateway API routing and Cloudflare Tunnel exposure.

## Non-Goals

- Do not expose wg-easy directly to the internet.
- Do not commit plaintext wg-easy credentials.
- Do not change WireGuard server defaults, AllowedIPs, DNS, or Gateway routes.

## Requirements

- **FR-001**: The access-broker ConfigMap MUST set `WGEASY_USERNAME`.
- **FR-002**: The access-broker Deployment MUST roll after the merged
  `homelab-access` PR #9 image publish.
- **FR-003**: Manifests MUST continue to use Gateway API and MUST NOT introduce
  Kubernetes `Ingress`.
- **FR-004**: Live manual approval smoke MUST be recorded as blocked until
  `WGEASY_PASSWORD` is added to `access-broker-secret`.

## Acceptance Criteria

- `kubectl kustomize kubernetes/apps/access-broker` renders with
  `WGEASY_USERNAME` and the new rollout annotation.
- Production render still includes `app-access-broker`.
- Plaintext scans show no wg-easy password in tracked manifests or artifacts.
- If the secret remains unavailable, evidence records the exact live-smoke
  blocker and substitute checks.
