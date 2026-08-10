# Implementation Plan: onepassword-dual-publish

**Branch**: `codex/onepassword-dual-publish` | **Date**: 2026-08-09

## Technical Context

**SDD Tier**: full/high-risk
**Workflow Risk Tier**: high
**Primary Areas**: 1Password item metadata, Kubernetes/Flux, secret-safe tooling, production validation
**Smoke Strategy**: exact-main Flux reconciliation followed by Ready and 17-pair byte-parity validation; no consumer smoke because consumers do not change
**Fanout**: none
**Exceptions**: The source inventory uses live Kubernetes metadata because Grafana SOPS MAC validation is broken. Values are never printed or persisted by tooling.

## Design

1. Store the 17 non-secret schemas in `tools/onepassword/production_items.json`.
2. Test and implement an authenticated resolver that verifies item metadata and writes ID-only manifests under `kubernetes/clusters/production/onepassword-items/`.
3. Add one production Flux Kustomization depending on `onepassword-operator` and every namespace owner. Production-only placement prevents the development service account from attempting production item IDs.
4. Test and implement a Kubernetes parity validator that reads both Secret objects into memory, compares type/key set/decoded bytes, and emits pair-level status only.
5. Reconcile the exact merged revision and require every item Ready plus 17/17 parity.

## Constitution Check

- [x] GitOps owns all durable Kubernetes resources.
- [x] Production foundation and rotation passed before dual publication.
- [x] SOPS and all consumers remain unchanged.
- [x] No Gateway, storage, or Talos behavior changes.
- [x] Secret values are excluded from Git, logs, arguments, and evidence.
- [x] Dedicated branch/worktree/PR used.

## TDD and Validation

- Unit tests first for inventory completeness, ID-only rendering, extra/missing fields, no-output failure handling, type/key/byte parity, and sentinel redaction.
- Render development and production roots; assert no `OnePasswordItem` in development.
- Run kubeconform, policy, architecture, harness, and full pre-commit.
- Diff-check 16 encrypted files, 17 decryption blocks, and all consumer references.
- Live: resolve items, reconcile exact main, wait 17 Ready items, run parity, record only counts/status/revisions.

## Research Decisions

- Official operator source maps non-empty item field labels directly to Secret keys, preserves Kubernetes-valid dots/underscores/uppercase, and supports `OnePasswordItem.type`.
- Secure Note items with empty notes and exact custom fields avoid unintended built-in Login fields.
- IDs in Git avoid ambiguous duplicate titles; item titles remain an operator-facing convention only.
