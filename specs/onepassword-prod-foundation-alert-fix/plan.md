# Implementation Plan: onepassword-prod-foundation-alert-fix

**Branch**: `codex/onepassword-prod-foundation-alert-fix` | **Date**: 2026-08-09

## Summary

Add a focused failing regression test, correct the alert/policy/runbook selector, run local checks, publish the minimal PR, then reconcile Grafana and validate the corrected PromQL against production.

## Workflow

**SDD Tier**: full artifacts, narrowly scoped corrective implementation
**Risk Tier**: high because the rule is production paging behavior
**Smoke Strategy**: live Grafana CR readiness plus Prometheus evaluation against the healthy Deployment
**Fanout**: none
**Exceptions**: No development deployment is needed; the defect is a production Helm-generated object-name mismatch discovered during the approved production smoke. The shared chart render and policy test provide pre-merge validation.

## Constitution Check

- [x] GitOps remains the source of truth.
- [x] No Secret or consumer state changes.
- [x] Production mutation is limited to reconciling the corrected monitoring resource.
- [x] Evidence remains metadata-only.
- [x] Dedicated branch/worktree/PR used.

## Validation

- Focused Python regression tests and policy checker
- Alerting Kustomize render and kubeconform
- Full pre-commit hooks
- Architecture check
- Post-merge Flux/Grafana reconciliation and live PromQL evaluation
