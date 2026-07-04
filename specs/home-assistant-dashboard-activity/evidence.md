# Evidence: home-assistant-dashboard-activity

**Branch**: `codex/home-assistant-dashboard-activity`
**Risk Tier**: medium
**Started**: 2026-07-04
**Owner**: implementation-agent-home-assistant-dashboard-activity

## Spec Kit Initialization

- Command: Not rerun; repository Spec Kit scaffolding already present on
  `origin/main`.
- Outcome: Used existing `.specify/` templates and constitution.
- Spec Kit version: Not changed by this implementation.
- Integration: Existing repository integration.
- Fallback: None.

## Workflow Validation

| Command | Result | Notes |
| ------- | ------ | ----- |
| `git remote set-url origin https://github.com/petebeegle/homelab.git && git fetch origin && git checkout -B codex/home-assistant-dashboard-activity origin/main` | PASS | Corrected implementation clone from stale local remote base `1750d60847d94c62bf4d0b5bc89d30cfc4a74cce` to current `origin/main` `c3c4210e349f90b1027b9a21944119303329fe02` before tracked edits. |
| `python3 tools/codex-harness/validate_active_implementation.py --marker .codex/tmp/active-implementation --root "$(pwd)" --branch "$(git branch --show-current)"` | PASS | Completed before tracked edits from corrected `origin/main` base. |
| `python3 tools/codex-harness/validate_implementation_plan.py --plan .codex/tmp/implementation-plan.yaml --marker .codex/tmp/active-implementation --root "$(pwd)" --branch "$(git branch --show-current)"` | PASS | Completed before tracked edits from corrected `origin/main` base. |
| `python3 tools/codex-harness/validate_workflow_attestations.py --kind owner --attestation .codex/tmp/implementation-owner-attestation.yaml --marker .codex/tmp/active-implementation --plan .codex/tmp/implementation-plan.yaml --root "$(pwd)" --branch "$(git branch --show-current)"` | PASS | Completed before tracked edits from corrected `origin/main` base. |

## Local Checks

| Command | Result | Notes |
| ------- | ------ | ----- |
| `python3 tools/codex-harness/validate_sdd_context.py --marker .codex/tmp/active-implementation --root "$(pwd)" --branch "$(git branch --show-current)" --require-plan-artifacts` | PASS | Completed after SDD bootstrap artifacts were created. |
| `jq empty kubernetes/infra/monitoring/grafana/dashboards/home-assistant-dashboard.json` | PASS | Dashboard JSON is valid. |
| `kubectl kustomize kubernetes/apps/home-assistant` | PASS | Production render includes `prometheus:` config and Service scrape annotations for `/api/prometheus`. |
| `kubectl kustomize kubernetes/apps/home-assistant/branch` | PASS | Branch render includes `prometheus:` config and Service scrape annotations for `/api/prometheus`. |
| `kubectl kustomize kubernetes/infra/monitoring/grafana/dashboards` | PASS | Dashboard ConfigMap render includes Activity panels and no removed Home Assistant dashboard panel titles. |
| `python3 tools/architecture/render.py --check` | PASS | Generated architecture document unchanged. |
| `python3 tools/codex-harness/validate_sdd_context.py --marker .codex/tmp/active-implementation --root "$(pwd)" --branch "$(git branch --show-current)" --require-plan-artifacts --require-evidence --head "$(git rev-parse HEAD)"` | PASS | Passed against final committed SDD evidence. |

## Development Validation

- Profile: manual
- Branch slug: `home-assistant-dashboard-activity`
- Validated commit: `f3259955819ede0664503a2733e63752bbd7c7e1` for the pushed
  development validation commit.
- Report path: N/A; helper output captured in command log.
- Cleanup: PASS; helper deleted
  `kustomization.kustomize.toolkit.fluxcd.io/branch-home-assistant-home-assistant-dashboard-activity`,
  waited for namespace `home-assistant-home-assistant-dashboard-activity`
  deletion, and deleted
  `gitrepository.source.toolkit.fluxcd.io/branch-home-assistant-home-assistant-dashboard-activity`.
- Prerequisite preparation:
  `.codex/scripts/prepare_development_smoke_secrets.sh home-assistant-dashboard-activity /workspaces/homelab-ideas/home-assistant-dashboard-activity`
  passed and installed the ignored development Terraform tfvars into the
  implementation clone without logging secret contents.
- Result or exception:
  `python3 tools/development/verify_branch_deploy.py --app home-assistant --branch codex/home-assistant-dashboard-activity --slug home-assistant-dashboard-activity --push`
  PASS. The helper pushed the branch, ran Terraform init/validate/plan,
  applied the branch Flux activation, reconciled GitRepository and
  Kustomization to
  `codex/home-assistant-dashboard-activity@sha1:f3259955819ede0664503a2733e63752bbd7c7e1`,
  confirmed namespace active, waited for the Home Assistant pod Ready
  condition, checked PVC, Service, and HTTPRoute resources, ran the in-cluster
  HTTP probe successfully, and cleaned up the branch Flux resources and
  namespace.

## Grafana/Mimir Query Smoke

- Query target: native `homeassistant_*` metrics after exporter enablement.
- Result or exception:
  `mcp__grafana.list_prometheus_metric_names(datasourceUid="prometheus", regex="^homeassistant_.*", startRfc3339="now-6h", endRfc3339="now")`
  returned `401 Unauthorized` while reading datasource UID `prometheus`.
  Substitute checks are the dashboard JSON validation, dashboard kustomize
  render, and rendered Home Assistant Service scrape annotations.

## Documentation Impact

- Updated: SDD artifacts under `specs/home-assistant-dashboard-activity/`.
- Generated docs: `docs/architecture.md` unchanged;
  `python3 tools/architecture/render.py --check` passed.
- No-docs rationale: No runbook or ADR changes are expected because this change
  follows existing Home Assistant, Grafana, Gateway, and monitoring patterns.

## Exceptions And Follow-Ups

- TDD exception: no practical red unit-test seam exists for this YAML and
  Grafana JSON-only change; focused render/schema checks are the substitute.
- Grafana/Mimir live query smoke is blocked by Grafana datasource authorization
  in this session (`401 Unauthorized` for datasource UID `prometheus`).

## Final State

- Final branch: `codex/home-assistant-dashboard-activity`.
- Final HEAD at verifier feedback:
  `33a42d3c99d06cb0d4ed83b4c37e35d89dac9fc6`.
- Evidence correction: this follow-up records the exact implementation-owner
  handoff commit above durably in tracked evidence after verifier feedback.
- Commit: `feat(home-assistant): add activity metrics dashboard`
- Verifier approval: not created by implementation owner.
