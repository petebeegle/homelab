# Implementation Plan: 1Password Development Cutover

**Branch**: `codex/onepassword-dev-cutover` | **Date**: 2026-08-10

## Technical Context

**SDD Tier**: full/high-risk
**Workflow Risk Tier**: high
**Primary Areas**: development Flux, cert-manager, Immich branch overlay, 1Password, secret-safe smoke tooling
**Smoke Strategy**: staging Certificate plus Immich profile with `--include-cluster-base`, followed by reversible deny-egress retention test
**Fanout**: none
**Exceptions**: Production is render/diff checked only; no production mutation.

## Design

1. Resolve three development item IDs from authenticated `op` metadata and render ID-only resources.
2. Add a development cert-manager overlay containing its `OnePasswordItem`; add a development certs overlay that patches both ClusterIssuers to the generated Secret.
3. Add two `OnePasswordItem` resources to the Immich branch overlay and patch every configuration/database reference to generated names.
4. Extend no-output parity tooling to accept the three-item development inventory.
5. Add automated disposable Certificate and outage-retention validators with guaranteed cleanup. The outage validator uses a temporary `CiliumNetworkPolicy` that permits only the `kube-apiserver` entity and restarts the stateless operator pod to force reconciliation while development polling is disabled.
6. Push the branch and run Immich smoke with sequential development-base reconciliation.

## Constitution Check

- [x] GitOps owns durable resources.
- [x] Development precedes production.
- [x] No plaintext Secret or token enters Git, state, arguments, or logs.
- [x] Existing SOPS rollback remains.
- [x] Production consumers and paths remain unchanged.
- [x] Dedicated branch/worktree/PR is used.

## Validation

- Unit tests for inventory/rendering, reference completeness, redaction, outage cleanup, and continuity assertions.
- Render/substitute both cluster roots and Immich branch overlay; kubeconform, policy, architecture, harness, pre-commit.
- Live 3/3 Ready/parity, disposable certificate, Immich API smoke, operator unavailability during the simulated vault outage, and operator/item recovery after egress restoration.

## Risks

- A dynamic Immich namespace could retain a legacy reference; render-level reference enumeration and live smoke fail closed.
- Cilium policy or cleanup failure could leave the operator unavailable; the validator uses guaranteed cleanup and verifies both operator and item recovery.
- UI entry may alter multiline/trailing bytes; parity blocks cutover.
