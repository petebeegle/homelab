# Implementation Plan: 1Password Alert Metric Label Fix

**SDD Tier**: full, narrowly scoped correction
**Risk Tier**: high production paging behavior
**Smoke Strategy**: exact PromQL evaluation through the in-cluster Mimir API after merge
**Fanout**: none

Add a failing live-label regression, update the PromQL and policy checker, run alert render/schema/pre-commit checks, publish the minimal PR, then reconcile Grafana and evaluate both expressions before the production canary.

## Constitution Check

- [x] GitOps owns the correction.
- [x] No Secret or consumer state changes.
- [x] Live evidence is metadata/metric-only.
- [x] Dedicated branch/worktree/PR used.
