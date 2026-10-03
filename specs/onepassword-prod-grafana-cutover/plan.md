# Implementation Plan: Production Grafana Credential Cutover

**Branch**: `codex/onepassword-prod-grafana-cutover` | **Date**: 2026-08-29 | **Spec**: `specs/onepassword-prod-grafana-cutover/spec.md`

**Input**: Feature specification from `specs/onepassword-prod-grafana-cutover/spec.md`

## Summary

Change only Grafana's admin and OAuth Secret references from `grafana-credentials` to the already-published `grafana-credentials-onepassword`. Keep `grafana-env`, the SOPS credential manifest, and Flux decryption unchanged. Enforce the narrow reference set with a repository policy test, prove no-output parity before merge, and perform the production rollout only after the PR merges. Automated health checks precede the user's Authentik login/dashboard smoke; a one-commit Grafana-only revert is the rollback.

## Technical Context

**Risk Tier**: high
**Workflow Tier**: high
**Primary Areas**: Kubernetes, Flux, Grafana HelmRelease, Grafana Operator external credentials, 1Password, policy tests
**Dependencies**: Flux, kubectl, Kustomize, kubeconform, Python unittest, existing 1Password parity validator, production Grafana synthetic smoke
**Storage**: No change
**Ingress**: Existing Gateway API `HTTPRoute` and `monitoring.lab.petebeegle.com`; no route change
**Secrets**: Retain SOPS `grafana-credentials` and `grafana-env`; consume only the existing ID-backed `grafana-credentials-onepassword`
**Smoke Strategy**: Existing synthetic login-shell probe plus post-merge `/api/health`, rollout/operator checks, and user-performed Authentik login/dashboard/data-source smoke
**Fanout Targets**: N/A; the implementation is a four-reference atomic change with one policy test surface
**Development Validation**: `smoke_profile: none` for Grafana because the development cluster intentionally omits the monitoring stack and production credentials. Substitute checks are strict production rendering, policy tests, current live no-output parity/readiness, existing synthetic coverage, and post-merge isolated production smoke with immediate revert.
**Post-Implementation SDD Conformance**: Local artifacts only; no workflow standard changes

## Human Gates

**Spec Gate**: Approved by the user with “get going” after review of the Grafana-only scope and manual smoke path.

**Checklist Status**: `checklists/requirements.md` passed 16/16 and `checklists/cutover.md` passed 14/14.

**Plan Gate**: Approved by the user with “go” on 2026-08-29.

**Expected Task/Analyze Gate**: Tasks plus Spec Kit analyze required before implementation.

## Constitution Check

*GATE: Must pass before tracked edits and be re-checked before commit.*

- [x] GitOps source of truth preserved; production changes apply only after merge.
- [x] No untracked production-first mutation; the documented development monitoring gap uses substitute checks and post-merge rollback.
- [x] Gateway API invariant preserved; the existing route is unchanged.
- [x] SOPS invariant preserved; no plaintext values are read into output or staged, and rollback manifests remain encrypted.
- [x] NFS default considered; no storage change exists.
- [x] Talos boundary preserved; no node operations exist.
- [x] Branch is `codex/onepassword-prod-grafana-cutover`; the established writable `/home/vscode/homelab-worktrees` fallback is used because `/workspaces/homelab-worktrees` is not writable.
- [x] Documentation impact is confined to SDD artifacts; the operator runbook already documents parity, rollback, and generated-Secret behavior.
- [x] PR review/status checks and the user's post-merge manual smoke are the review gates.

## Project Structure

### SDD Artifacts

```text
specs/onepassword-prod-grafana-cutover/
├── checklists/requirements.md
├── data-model.md
├── evidence.md
├── plan.md
├── quickstart.md
├── research.md
├── spec.md
└── tasks.md
```

### Source Or Documentation Changes

```text
kubernetes/infra/monitoring/grafana/app.yaml
kubernetes/infra/monitoring/grafana/grafana-instance.yaml
tools/policy/check_onepassword_production_foundation.py
tools/policy/tests/test_check_onepassword_production_foundation.py
specs/onepassword-prod-grafana-cutover/*
```

## Tiered TDD And Validation Plan

**TDD expectation**: First add a failing policy test requiring all four Grafana admin/OAuth references to use `grafana-credentials-onepassword` while `envFromSecret` remains `grafana-env` and the SOPS manifest remains included. Then update only the two Grafana manifests.

**Local checks**:

- `python3 -m unittest tools.policy.tests.test_check_onepassword_production_foundation`
- `python3 tools/policy/check_onepassword_production_foundation.py`
- `kubectl kustomize kubernetes/clusters/production | flux envsubst --strict`
- `kubeconform` against the strict production render through the repository validation path
- `python3 tools/architecture/render.py --check`
- `python3 -m unittest discover -s tools/codex-harness/tests`
- `pre-commit run --all-files`

**Development smoke**: None. The binding development runbook records monitoring/Grafana as a coverage gap because the development cluster intentionally omits the monitoring stack and its credentials. No production mutation occurs before merge.

**Automated smoke preference**: Before merge, require the existing production synthetic Grafana route check to be healthy and record no-output parity/readiness. After merge, require Flux fetched/applied SHA, Helm rollout, Grafana and dashboard-operator health, `/api/health`, existing route synthetic health, then manual Authentik login and a known dashboard with live data.

**Completion evidence**: Record the merge SHA, Flux fetched/applied revisions, all four live Secret reference names, generated item readiness, no-output parity, rollout/pod UID, Grafana CR health, HTTPRoute status, `/api/health`, synthetic status, user's manual result, and whether rollback was needed.

**Fanout plan**: None; keep the credential-reference change and policy invariant sequential and consolidate all results in `evidence.md`.

**Evidence destination**: `specs/onepassword-prod-grafana-cutover/evidence.md` and a post-merge PR comment for live deployment evidence.

## Documentation Impact

No canonical runbook or ADR change is required. The existing 1Password runbook already defines generated Secret safety and rollback. This implementation records its consumer-specific smoke and rollback in the SDD artifacts.

## Implementation Steps

1. Add a failing repository policy test for the exact Grafana generated/legacy reference boundary.
2. Change the Helm admin Secret, OAuth mount Secret, and Grafana Operator admin username/password Secret references to `grafana-credentials-onepassword`.
3. Confirm `grafana-env`, both SOPS manifests, Flux decryption, routes, dashboards, alerts, data sources, and all non-Grafana consumers are unchanged.
4. Run strict local validation and current live read-only readiness/parity checks; open a gated PR.
5. After explicit merge approval, reconcile production through Flux and run automated Grafana health/rollout/operator/synthetic checks.
6. Hand off the exact manual Authentik login/dashboard/data-source smoke. If any acceptance check fails, revert the Grafana cutover commit and reconcile; never delete the `OnePasswordItem`.

## Risks

| Risk | Mitigation |
| ---- | ---------- |
| A missed Grafana credential reference creates partial authentication failure | Policy test enumerates Helm admin, OAuth mount, and both Grafana Operator references. |
| Generated bytes differ from the live legacy Secret | Require no-output key/byte parity and Ready=True immediately before merge. |
| Grafana fails to roll out | Keep one replica change isolated, wait ten minutes, and revert the single commit if readiness fails. |
| OAuth login fails while anonymous health passes | User must complete the existing Authentik login path before acceptance. |
| Dashboard Operator loses admin access | Verify Grafana CR and managed dashboard/resource reconciliation after rollout. |
| Notification delivery changes accidentally | Require `envFromSecret: grafana-env`; do not edit `grafana-env` references or manifests. |
| Production-only validation lacks a development equivalent | Document the binding coverage gap, use broad local/read-only checks, and mutate production only through a merged, immediately revertible GitOps commit. |

## Complexity Tracking

No constitution violations require justification.
