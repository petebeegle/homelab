# Evidence: immich-app

**Branch**: `codex/immich-app`
**Risk Tier**: high
**Started**: 2026-07-04

## Spec Kit Initialization

- Command: manual artifact bootstrap from repo templates in fallback worktree
- Outcome: PASS
- Spec Kit version: not changed
- Integration: existing repository Spec Kit/Codex integration
- Fallback: `/workspaces/homelab-worktrees` was not writable, so the
  implementation worktree is `/workspaces/homelab-ideas/immich-app`.

## Workflow Validation

| Command | Result | Notes |
| ------- | ------ | ----- |
| `git status --short --branch` | PASS | Branch `codex/immich-app`. |

## Local Checks

| Command | Result | Notes |
| ------- | ------ | ----- |
| `sops -d kubernetes/apps/immich/secret.yaml >/dev/null && sops -d kubernetes/infra/authentik/secret.yaml >/dev/null` | PASS | Changed secret manifests decrypt locally. |
| `kubectl kustomize kubernetes/apps/immich >/tmp/immich-app-render.yaml` | PASS | Failed once on obsolete `vars` config, fixed by removing unused `kustomizeconfig.yaml`; final render confirms stable `immich-values` ConfigMap reference. |
| `kubectl kustomize kubernetes/infra/monitoring/grafana >/tmp/grafana-render.yaml` | PASS | Immich folder/dashboard render. |
| `kubectl kustomize kubernetes/infra/controllers/local-path-provisioner >/tmp/local-path-render.yaml` | PASS | Remote local-path base and patches render. |
| `kubectl kustomize kubernetes/clusters/production >/tmp/production-render.yaml` | PASS | Production Flux graph renders. |
| `kubectl kustomize kubernetes/clusters/development >/tmp/development-render.yaml` | PASS | Development Flux graph renders. |
| `helm template immich oci://ghcr.io/immich-app/immich-charts/immich --version 0.13.1 -f kubernetes/apps/immich/values.yaml >/tmp/immich-helm-template.yaml` | PASS | Failed once on invalid `controllers.mainAnnotations`, fixed by removing that unsupported value. |
| `npm --prefix kubernetes/apps/synthetics/smoke ci` | PASS | Installed smoke test dependencies from lockfile. |
| `npm --prefix kubernetes/apps/synthetics/smoke run test:unit` | PASS | 5 unit tests passed. |
| `terraform -chdir=terraform/development init -backend=false -input=false && terraform -chdir=terraform/development validate` | PASS | Valid with existing Proxmox provider deprecation warnings. |
| `terraform -chdir=terraform/production init -backend=false -input=false && terraform -chdir=terraform/production validate` | PASS | Valid with existing Proxmox provider deprecation warnings. |
| `python3 tools/architecture/render.py --write && python3 tools/architecture/render.py --check` | PASS | Updated generated architecture inventory. |

## Automated Smoke And Live Verification

| Target | Method | Result | Notes |
| ------ | ------ | ------ | ----- |
| `https://immich.${cluster_domain}` | Playwright route test | PARTIAL | Test added. Local full smoke cannot prove Immich until GitOps deploys it; the local suite skipped Immich on 404. |
| `https://lab.petebeegle.com/` | `npm --prefix kubernetes/apps/synthetics/smoke test` | BLOCKED | Local runner cannot resolve `lab.petebeegle.com`; one root Homepage test failed with `net::ERR_NAME_NOT_RESOLVED`, 7 passed, 1 skipped. |

## Deployment State

- Source fetched SHA:
- Target applied SHA:
- Live resource spec checked:
- Gateway/listener/DNS/certificate checked:
- Exact user-facing URL result: not checked; live DNS/service path unavailable from this local runner before GitOps deploy.

## Development Validation

- Profile: manual/base
- Branch slug: immich-app
- HEAD: `ad0d5454dfdb44b1bdd1d54ad5ad89985aaf2c04`
- Report path: local command output only
- Cleanup: removed local `node_modules`, Playwright `test-results`, Terraform `.terraform`, and Python `__pycache__` artifacts created during validation
- Result or exception: Cluster manifests render for development and production. Exact routed browser smoke is unavailable locally because `lab.petebeegle.com` does not resolve here and Immich is not yet reconciled in the live cluster.

## Documentation Impact

- Updated: `docs/runbooks/immich.md`
- Generated docs: `docs/architecture.md`
- No-docs rationale: N/A

## SDD Conformance

- Local sources checked: `AGENTS.md`,
  `docs/runbooks/spec-driven-development.md`,
  `docs/runbooks/implementation-workflow.md`
- Upstream Spec Kit sources checked: local skill templates
- Spec -> Plan -> Tasks -> Implement alignment: complete
- Artifact updates after implementation: complete

## Exceptions And Follow-Ups

- Worktree path exception: `/workspaces/homelab-worktrees` was not writable, so implementation used `/workspaces/homelab-ideas/immich-app`.
- Live smoke exception: exact Immich user path requires Flux reconciliation and routable homelab DNS; local full smoke was blocked at DNS for the root domain.
- Follow-up after merge/reconcile: check Flux `infra-cloudnative-pg`, `infra-local-path-provisioner`, `app-immich`; verify `immich-postgres` readiness; run the synthetic smoke job; confirm Grafana dashboard panels populate from Alloy-scraped Immich metrics.

## Final State

- Final branch: `codex/immich-app`
- Final HEAD: `ad0d5454dfdb44b1bdd1d54ad5ad89985aaf2c04`
- Commit: local conventional commit created after validation.
