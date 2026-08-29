# Evidence: Production Grafana Credential Cutover

## Human Gates And Scope

- Spec gate: approved by the user with “get going”.
- Plan gate: approved by the user with “go” on 2026-08-29.
- Task/analyze gate: approved by the user with “yep” after review of the one
  analysis finding and proposed remediation.
- Risk tier: high.
- Intended source boundary: four `grafana-credentials` references only; retain
  `grafana-env`, encrypted SOPS resources, Flux decryption, and all other
  production consumer references.
- Worktree exception: `/workspaces/homelab-worktrees` was not writable, so the
  established `/home/vscode/homelab-worktrees/onepassword-prod-grafana-cutover`
  fallback is used.

## Pre-Implementation State

Captured read-only on 2026-08-29 before implementation:

- Flux source and `monitoring` Kustomization: Ready=True at
  `main@sha1:c8cdd4cbfc4268c16d32a5b1266f5be74f84c922`.
- Grafana HelmRelease: Ready=True; Deployment: 1/1 ready and available;
  pre-change pod UID: `a5cf86e4-46e9-4d2c-8c54-c490e6153d0c`.
- `grafana/grafana-credentials-onepassword`: Ready=True. The item path was
  inspected as an ID-only vault/item reference; no token or field value was
  output.
- The no-output parity validator passed all 17 inventory pairs, including
  `grafana/grafana-credentials -> grafana-credentials-onepassword`.
- Live pre-change references: Helm admin and OAuth mount plus Grafana external
  admin username/password all used `grafana-credentials`; Helm
  `envFromSecret` used `grafana-env`.
- Grafana custom resource: `GrafanaReady=True`, stage `complete`, status
  `success`, version `12.3.2`.
- `monitoring-radar` dashboard: `DashboardSynchronized=True`; all 12 managed
  dashboards were present.
- HTTPRoute `grafana/monitoring`: Accepted=True, ResolvedRefs=True, hostname
  `monitoring.lab.petebeegle.com`.
- Latest scheduled synthetic Job `synthetic-smoke-29800620`: succeeded with
  `SMOKE_RUN_SUMMARY status=success failed_count=0` (11 tests passed).

## Spec Kit Analysis

- Requirements analyzed: FR-001 through FR-009 and SC-001 through SC-006.
- Task count: 21 total; six User Story 1 tasks and one User Story 2 task, with
  setup, verification, PR, and post-merge acceptance tasks covering the shared
  requirements.
- Coverage: 15/15 requirements and measurable success criteria mapped to tasks.
- Constitution conflicts: none.
- Finding resolved: the manual-smoke timing assumption was clarified to require
  smoke after merge and before acceptance, matching the GitOps rollout plan.

## TDD And Local Validation

- Red: `python3 -m unittest tools.policy.tests.test_check_onepassword_production_foundation`
  failed because `check_grafana_cutover_boundary` did not yet exist.
- Intermediate red: after adding the checker, the repository policy test
  reported the two legacy Helm and two legacy Grafana external references.
- Green: the same focused suite passed 7/7 after changing exactly those four
  references.
- `python3 tools/policy/check_onepassword_production_foundation.py`: passed.
- `git diff --check`: passed.
- Strict Flux substitution of both production and development cluster renders:
  passed after binding only `var` to an ephemeral placeholder. Both upstream
  CRD renders contain a documentation example using literal `${var...}` syntax,
  which strict substitution otherwise treats as a deployment variable.
- Kubeconform 0.7.0 over both substituted cluster renders: 122 resources,
  44 valid, 0 invalid, 0 errors, and 78 skipped for missing schemas.
- `python3 tools/architecture/render.py --check`: passed.
- `python3 -m unittest discover -s tools/codex-harness/tests`: passed 81/81.
- `pre-commit run --all-files`: all hooks passed, including yamllint,
  k8svalidate, architecture, production 1Password policy, and migration safety.
- Source-boundary review: the YAML behavior diff contains exactly four
  `grafana-credentials -> grafana-credentials-onepassword` reference changes.
  `envFromSecret: grafana-env`, routes, alerts, data sources, dashboards,
  encrypted `secret.yaml` and `grafana-env.yaml`, production `sops-age`
  decryption, and all non-Grafana consumers are unchanged.

## Development Validation Exception

Development intentionally omits monitoring/Grafana and production credentials.
The approved substitute strategy is strict production rendering and policy
validation, live read-only generated-item readiness and no-output parity, current
synthetic health, and a post-merge isolated production rollout with immediate
Git revert available.

Substitute local validation passed as recorded above; no development-cluster
mutation was attempted because the approved monitoring coverage exception
applies.

## Pre-Merge Production Read-Only Checks

Repeated at `2026-08-29T21:18:12Z`:

- Flux source and `monitoring` remained Ready=True at
  `main@sha1:c8cdd4cbfc4268c16d32a5b1266f5be74f84c922`.
- Generated item, Grafana HelmRelease, and 1/1 Deployment remained ready.
- Grafana custom resource remained `GrafanaReady=True`, stage `complete`, status
  `success`; 12 dashboards were present with zero unsynchronized.
- HTTPRoute remained Accepted=True and ResolvedRefs=True.
- `https://monitoring.lab.petebeegle.com/api/health` reported database `ok` and
  Grafana `12.3.2`.
- Latest scheduled synthetic Job `synthetic-smoke-29800635` succeeded.
- The no-output parity validator again passed 17/17 Secret pairs.

Spec Kit convergence checked all 15 requirements/success criteria, both user
stories, approved plan decisions, and seven constitution principles. It found
no missing, partial, contradictory, or unrequested work and appended no tasks.

The final constitution re-check passed: GitOps remains the only mutation path;
Gateway, encrypted-secret, storage, and Talos boundaries are unchanged; the
development-monitoring exception and substitute evidence satisfy the risk gate;
and the implementation remains branch/worktree/PR scoped.

## Commit And Pull Request

Pending.

## Post-Merge Reconciliation And Automated Smoke

Pending explicit merge approval.

## Manual Smoke

Pending user validation at `https://monitoring.lab.petebeegle.com`.

## Rollback And Cleanup

The desired-state behavior change is confined to four references in
`kubernetes/infra/monitoring/grafana/app.yaml` and
`kubernetes/infra/monitoring/grafana/grafana-instance.yaml`. Reverting the
cutover commit restores all four to `grafana-credentials`; the Kustomization
continues to include `secret.yaml` and `grafana-env.yaml`, and production
monitoring continues to decrypt with `sops-age`. Never delete the generated
Secret or `OnePasswordItem` as rollback.
