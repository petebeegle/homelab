# Implementation Plan: onepassword-prod-foundation

**Branch**: `codex/onepassword-prod-foundation` | **Date**: 2026-08-09 | **Spec**: `specs/onepassword-prod-foundation/spec.md`

## Summary

Activate the development-proven shared 1Password Operator in the production Flux base. Configure production Terraform bootstrap for `dual` trust roots through a production-specific non-secret `op://` reference, extend kube-state-metrics with metadata-only `OnePasswordItem` readiness, and add Grafana alerts for operator and item health. Preserve every SOPS resource and consumer reference, then prove the isolated production path with the existing disposable canary.

## Technical Context

**SDD Tier**: full/high-risk
**Workflow Risk Tier**: high
**Primary Areas**: Kubernetes, Flux, Terraform bootstrap, monitoring, production validation, documentation
**Dependencies**: Existing chart `connect` 2.4.1/operator 1.12.0 manifests, Flux controllers, kube-state-metrics 6.3.0, Grafana Operator alert rules, authenticated 1Password CLI, kubectl
**Secrets**: Production remains `dual`. Terraform carries only `op://cluster bootstrap/onepassword-production-operator/credential`; the shared helper reads the token into a mode-0600 temporary file. No value is rendered or stored in state.
**Smoke Strategy**: Local dual-cluster validation, development regression checks, then a production-only disposable canary using `cluster production`
**Fanout Targets**: None; no sub-agent work was requested and the changes converge on shared monitoring/configuration files
**Exceptions**: The normal development-first requirement is satisfied by merged phase-1 live evidence. Production mutation is limited to this explicitly approved foundation and canary.

## Human Gates

**Spec Gate**: Approved by the user through the supplied phased plan and “merged. next”.

**Clarify Gate**: Passed with zero questions; no material ambiguity remains.

**Plan Gate**: Approved within the exact phase-2 scope already supplied by the user.

**Task/Analyze Gate**: Proceed when the read-only cross-artifact analysis finds no critical/high issue.

## Constitution Check

- [x] GitOps owns all durable cluster state; only bootstrap Secrets and canary validation are imperative exceptions.
- [x] Development-first validation is recorded in merged phase-1 evidence.
- [x] SOPS/Age and all consumer references remain active.
- [x] No Gateway, storage, or Talos invariant is affected.
- [x] Production token isolation and no-output requirements are explicit.
- [x] Work is isolated on `codex/onepassword-prod-foundation` in a sibling worktree.
- [x] Architecture generation and runbook impact are included.
- [x] PR checks remain the review gate.

## Project Structure

```text
specs/onepassword-prod-foundation/
├── checklists/
├── contracts/
├── data-model.md
├── evidence.md
├── plan.md
├── quickstart.md
├── research.md
├── spec.md
└── tasks.md

terraform/production/{main.tf,variables.tf,README.md}
kubernetes/clusters/production/infra/{kustomization.yaml,onepassword-operator.yaml}
kubernetes/infra/monitoring/kube-state-metrics/config/metrics.yaml
kubernetes/infra/monitoring/grafana/alerting/{kustomization.yaml,alert-rules-onepassword.yaml}
tools/policy/check_onepassword_production_foundation.py
tools/policy/tests/test_check_onepassword_production_foundation.py
docs/runbooks/onepassword-operator.md
docs/architecture.md
```

## TDD and Validation

Add a failing focused policy test first. It will assert production operator activation, dual bootstrap wiring and reference isolation, SOPS consumer preservation, metadata-only KSM configuration, and both ten-minute alert rules. Then implement the manifests/configuration.

Local acceptance:

- Focused production-foundation policy unit tests
- Existing bootstrap and canary unit tests
- `bash -n` for bootstrap scripts and the chart policy check
- Terraform format/validate and generated production README
- Strict substitutions/renders of development and production entrypoints
- kubeconform for both renders
- chart policy assertion proving no Connect/token Secret
- repository policy, architecture, harness, and affected unit tests
- diff-based assertion that existing SOPS manifests, decryption blocks, and consumer Secret references do not change

Live acceptance:

1. From an authenticated user session, install both production bootstrap trust roots with `FLUX_BOOTSTRAP_SECRET_PROVIDER=dual`.
2. Reconcile production at the exact branch revision and verify fetched/applied revisions plus Kustomization, HelmRelease, and Deployment readiness.
3. Run `verify_onepassword_operator.py` with `cluster production`, the production canary item, production kubeconfig, and a unique slug.
4. Record only Secret resource-version and pod-UID transitions; confirm namespace cleanup.
5. Confirm existing SOPS consumers and running workloads remain Ready.

**Evidence destination**: `specs/onepassword-prod-foundation/evidence.md`.

## Documentation Impact

- Add production bootstrap, isolated service-account, canary, safety, and rollback instructions to a dedicated operator runbook.
- Regenerate `docs/architecture.md` for the production operator Kustomization.
- Leave the secrets ADR, constitution, and `AGENTS.md` migration policy changes for SOPS retirement.

## Risks

| Risk | Mitigation |
| --- | --- |
| Production token is accidentally shared with development or leaked | Separate vault/service account/reference; use the proven file-based `op read` helper and metadata-only evidence. |
| Operator activation disrupts existing workloads | Add only a new controller; retain SOPS and change zero consumer references. |
| Missing resources appear healthy in alerts | Explicitly alert on absent operator Deployment and non-True/missing item readiness. |
| Monitoring RBAC exposes data | Grant only list/watch/get for `OnePasswordItem`; export metadata and Ready condition only. |
| Canary cleanup deletes a generated Secret | Use a unique disposable namespace/item only; document `OnePasswordItem` deletion semantics. |

## Complexity Tracking

No constitution violation requires justification.
