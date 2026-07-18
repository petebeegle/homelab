# Feature Specification: access-broker-wgeasy-password

**Feature Branch**: `codex/access-broker-wgeasy-password`
**Date**: 2026-07-18
**SDD Tier**: medium

## Intent Brief

Complete access-broker wg-easy provisioning by adding the operator-provided
wg-easy password to the access-broker SOPS Secret without exposing the plaintext
value to Codex or committing it unencrypted.

## Requirements

- **FR-001**: `kubernetes/apps/access-broker/secret.yaml` MUST include
  `WGEASY_PASSWORD` as a SOPS-encrypted `stringData` key.
- **FR-002**: No plaintext wg-easy password or WireGuard config material may be
  committed.
- **FR-003**: Rendered access-broker manifests MUST continue to use the existing
  Gateway API route and MUST NOT introduce Kubernetes `Ingress`.

## Acceptance Criteria

- `sops filestatus kubernetes/apps/access-broker/secret.yaml` reports encrypted.
- Access-broker package render includes `WGEASY_PASSWORD` only as encrypted
  secret data.
- Plaintext scans pass for known secret markers.
