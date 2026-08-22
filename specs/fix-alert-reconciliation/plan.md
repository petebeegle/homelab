# Implementation Plan: Fix Alert Reconciliation

**Branch**: `codex/fix-alert-reconciliation` | **Risk Tier**: high

## Technical Context

**Primary Areas**: Flux post-build substitution, Grafana dashboard JSON.

**Smoke Strategy**: strict local production render, then post-merge production Flux and alert-state verification.

**Exceptions**: Development does not operate this production Grafana instance; production verification is required after merge.

## Constitution Check

- [x] Desired state is changed only in Git.
- [x] No Secret value or live configuration is edited.
- [x] Alert semantics remain unchanged.
- [x] The separate private-source failure is isolated in PR 43.

## Steps

1. Escape only the three Grafana dashboard datasource placeholders.
2. Render the Grafana Kustomization with production substitutions and strict envsubst.
3. Run JSON/YAML and generated-architecture checks.
4. Commit, push, and open a PR.
5. After merge, verify Flux, private-source dependencies, and active alert state.
