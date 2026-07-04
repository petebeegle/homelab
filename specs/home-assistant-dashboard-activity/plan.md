# Implementation Plan: home-assistant-dashboard-activity

**Branch**: `codex/home-assistant-dashboard-activity` | **Date**: 2026-07-04 | **Spec**:
`specs/home-assistant-dashboard-activity/spec.md`

**Input**: Feature specification from `specs/home-assistant-dashboard-activity/spec.md`

## Summary

Enable Home Assistant's native Prometheus exporter for the production and branch
apps, annotate the Services for internal scraping, and update the Home
Assistant Grafana dashboard to replace synthetic smoke-specific panels with a
native Prometheus-backed Activity section while preserving operational health
and log panels.

## Technical Context

**Risk Tier**: medium
**Workflow Tier**: medium
**Primary Areas**: Kubernetes app manifests, branch overlay, Grafana dashboard,
SDD evidence
**Dependencies**: kubectl kustomize, jq, Python architecture renderer, Codex
harness validators, development branch deploy helper, Grafana/Mimir access if
available
**Storage**: Existing Home Assistant PVC remains on the configured storage;
this change does not alter PVCs or StorageClasses.
**Ingress**: Gateway API invariant preserved; no `Ingress`, HTTPRoute, TLSRoute,
or external route changes.
**Secrets**: SOPS invariant preserved; no secrets are read, created, or edited.
**Development Validation**: attempt
`python3 tools/development/verify_branch_deploy.py --app home-assistant --branch codex/home-assistant-dashboard-activity --slug home-assistant-dashboard-activity --push`;
record exact exception and substitute checks if prerequisites are unavailable.

## Constitution Check

*GATE: Must pass before tracked edits and be re-checked before commit.*

- [x] GitOps source of truth preserved; no durable live-cluster-only state.
- [x] No production-first mutation; development validation plan or exception is
      recorded for covered changes.
- [x] Gateway API invariant preserved; no new Kubernetes `Ingress` resources.
- [x] SOPS invariant preserved; no plaintext secret manifests staged.
- [x] NFS default considered for PVC-backed workloads.
- [x] Talos boundary preserved; no SSH-based node operations introduced.
- [x] Branch is `codex/home-assistant-dashboard-activity`; sibling clone
      ownership files were validated before tracked edits.
- [x] Documentation impact identified; SDD artifacts document the behavior and
      generated architecture is checked.
- [x] PR review/status checks are the review gate; verifier approval is not
      created by the implementation owner.

## Project Structure

### SDD Artifacts

```text
specs/home-assistant-dashboard-activity/
├── spec.md
├── plan.md
├── tasks.md
└── evidence.md
```

### Source Or Documentation Changes

```text
kubernetes/apps/home-assistant/config/configuration.yaml
kubernetes/apps/home-assistant/branch/config/configuration.yaml
kubernetes/apps/home-assistant/service.yaml
kubernetes/apps/home-assistant/branch/home-assistant.yaml
kubernetes/infra/monitoring/grafana/dashboards/home-assistant-dashboard.json
specs/home-assistant-dashboard-activity/
```

## Tiered TDD And Validation Plan

**TDD expectation**: There is no practical red unit-test seam for a Grafana JSON
dashboard and Kubernetes YAML-only configuration change. Use focused render and
schema checks as the medium-tier substitute, and document the exception in
evidence.

**Local checks**:

- `python3 tools/codex-harness/validate_active_implementation.py --marker .codex/tmp/active-implementation --root "$(pwd)" --branch "$(git branch --show-current)"`
- `python3 tools/codex-harness/validate_implementation_plan.py --plan .codex/tmp/implementation-plan.yaml --marker .codex/tmp/active-implementation --root "$(pwd)" --branch "$(git branch --show-current)"`
- `python3 tools/codex-harness/validate_workflow_attestations.py --kind owner --attestation .codex/tmp/implementation-owner-attestation.yaml --marker .codex/tmp/active-implementation --plan .codex/tmp/implementation-plan.yaml --root "$(pwd)" --branch "$(git branch --show-current)"`
- `python3 tools/codex-harness/validate_sdd_context.py --marker .codex/tmp/active-implementation --root "$(pwd)" --branch "$(git branch --show-current)" --require-plan-artifacts`
- `jq empty kubernetes/infra/monitoring/grafana/dashboards/home-assistant-dashboard.json`
- `kubectl kustomize kubernetes/apps/home-assistant`
- `kubectl kustomize kubernetes/apps/home-assistant/branch`
- `kubectl kustomize kubernetes/infra/monitoring/grafana/dashboards`
- `python3 tools/architecture/render.py --check`
- `python3 tools/codex-harness/validate_sdd_context.py --marker .codex/tmp/active-implementation --root "$(pwd)" --branch "$(git branch --show-current)" --require-plan-artifacts --require-evidence --head "$(git rev-parse HEAD)"`

**Development smoke**: Attempt the Home Assistant branch deployment helper with
`--push` after local checks pass. If kubeconfig, cluster credentials, staged
secrets, or network prerequisites are unavailable, record the exact blocker and
substitute local kustomize/dashboard checks.

**Evidence destination**: `specs/home-assistant-dashboard-activity/evidence.md`
and `.codex/tmp/pr-summary.md`.

## Documentation Impact

- SDD artifacts document the accepted plan, source-doc rationale, validation,
  and exceptions.
- `docs/architecture.md` is expected to remain unchanged because the app,
  route, and storage topology do not change; run
  `python3 tools/architecture/render.py --check` and update generated
  architecture only if it reports drift.

## Implementation Steps

1. Create workflow files and durable SDD artifacts from the corrected
   `origin/main` base.
2. Enable the Home Assistant Prometheus exporter in production and branch
   configuration.
3. Annotate production and branch Home Assistant Services for internal
   Prometheus scraping.
4. Update the Grafana dashboard JSON by removing the requested synthetic
   smoke/pod phase panels and adding the Activity row and native
   Home Assistant Prometheus panels.
5. Run local validation, architecture check, SDD validators, development smoke
   attempt, and live metric query smoke attempt.
6. Record evidence, write `.codex/tmp/pr-summary.md`, and commit with a
   conventional commit message.

## Risks

| Risk | Mitigation |
| ---- | ---------- |
| Dashboard queries reference metrics before Home Assistant has restarted and Prometheus has scraped them. | Use `OR vector(0)` or table queries that tolerate absent series and record live query smoke availability. |
| `requires_auth: false` exposes the exporter if routing changes later. | Keep exposure limited to internal Service scraping annotations; no external route changes are included. |
| Development branch deploy requires unavailable cluster credentials or secret staging. | Attempt the helper and record the exact exception plus substitute local renders. |
| Home Assistant exporter omits unavailable or unknown entities after startup. | Include `homeassistant_entity_available` and document that activity is Prometheus-derived rather than Logbook prose. |

## Complexity Tracking

> Fill only when the constitution check has a violation that must be justified.

| Violation | Why Needed | Simpler Alternative Rejected Because |
| --------- | ---------- | ------------------------------------ |
| N/A | N/A | N/A |
