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
| `sops -d kubernetes/apps/immich/base/secret.yaml >/dev/null && sops -d kubernetes/infra/authentik/secret.yaml >/dev/null` | PASS | Changed secret manifests decrypt locally. |
| `kubectl kustomize kubernetes/apps/immich >/tmp/immich-app-render.yaml` | PASS | Failed once on obsolete `vars` config, fixed by removing unused `kustomizeconfig.yaml`; final render confirms stable `immich-values` ConfigMap reference. |
| `branch_slug=immich-app cluster_domain=dev.lab.petebeegle.com kubectl kustomize kubernetes/apps/immich/branch \| flux envsubst --strict >/tmp/immich-branch-render.yaml` | PASS | Branch overlay renders with `immich-immich-app` namespace and no unsubstituted placeholders. |
| `kubectl kustomize kubernetes/infra/monitoring/grafana >/tmp/grafana-render.yaml` | PASS | Immich folder/dashboard render. |
| `kubectl kustomize kubernetes/infra/controllers/local-path-provisioner >/tmp/local-path-render.yaml` | PASS | Remote local-path base and patches render; dev smoke changed node path from read-only `/var/mnt/local-path-provisioner` to writable `/var/local-path-provisioner`. |
| `kubectl kustomize kubernetes/clusters/production >/tmp/production-render.yaml` | PASS | Production Flux graph renders. |
| `kubectl kustomize kubernetes/clusters/development >/tmp/development-render.yaml` | PASS | Development Flux graph renders. |
| `helm template immich oci://ghcr.io/immich-app/immich-charts/immich --version 0.13.1 -f kubernetes/apps/immich/base/values.yaml >/tmp/immich-helm-template.yaml` | PASS | Failed once on invalid `controllers.mainAnnotations`, fixed by removing that unsupported value. |
| `npm --prefix kubernetes/apps/synthetics/smoke ci` | PASS | Installed smoke test dependencies from lockfile. |
| `npm --prefix kubernetes/apps/synthetics/smoke run test:unit` | PASS | 5 unit tests passed. |
| `terraform -chdir=terraform/development init -backend=false -input=false && terraform -chdir=terraform/development validate` | PASS | Valid with existing Proxmox provider deprecation warnings. |
| `terraform -chdir=terraform/production init -backend=false -input=false && terraform -chdir=terraform/production validate` | PASS | Valid with existing Proxmox provider deprecation warnings. |
| `python3 tools/architecture/render.py --write && python3 tools/architecture/render.py --check` | PASS | Updated generated architecture inventory. |

## Automated Smoke And Live Verification

| Target | Method | Result | Notes |
| ------ | ------ | ------ | ----- |
| `https://immich-immich-app.dev.lab.petebeegle.com/api/server/ping` | Manual development Flux smoke through Gateway | PASS | Branch source fetched `59f3a055905566857496c1c974a6a5d54d09a351`; temporary dev base Kustomizations installed `local-path-provisioner` and `cloudnative-pg`; `branch-immich-immich-app` applied; Gateway curl with `--resolve` to dev internal Gateway returned `{"res":"pong"}`. |
| `http://immich-server.immich-immich-app.svc.cluster.local:2283/api/server/ping` | In-cluster service probe | PASS | Curl probe pod in `immich-immich-app` returned `{"res":"pong"}`. |
| `https://immich.${cluster_domain}` | Production Playwright route test | PENDING | Test added; production smoke remains post-merge/reconcile work. |
| `https://lab.petebeegle.com/` | `npm --prefix kubernetes/apps/synthetics/smoke test` | BLOCKED | Local runner cannot resolve `lab.petebeegle.com`; one root Homepage test failed with `net::ERR_NAME_NOT_RESOLVED`, 7 passed, 1 skipped. |

## Deployment State

- Source fetched SHA: development branch `codex/immich-app@sha1:59f3a055905566857496c1c974a6a5d54d09a351`
- Target applied SHA: `branch-immich-immich-app` applied `codex/immich-app@sha1:59f3a055905566857496c1c974a6a5d54d09a351`
- Live resource spec checked: `HelmRelease/immich=True`, `Cluster/immich-postgres` healthy, pods Ready, `immich-library` Bound on `nfs-csi-media-storage`, `immich-postgres-1` Bound on `local-path`, `HTTPRoute/immich` `Accepted=True` and `ResolvedRefs=True`
- Gateway/listener/DNS/certificate checked: dev internal Gateway path checked with `curl --resolve immich-immich-app.dev.lab.petebeegle.com:443:192.168.30.225`
- Exact user-facing URL result: `https://immich-immich-app.dev.lab.petebeegle.com/api/server/ping` returned `{"res":"pong"}` through the dev Gateway.

## Development Validation

- Profile: manual/immich
- Branch slug: immich-app
- HEAD: `59f3a055905566857496c1c974a6a5d54d09a351`
- Report path: `.codex/tmp/immich-dev-smoke-20260704T181647Z.log`
- Cleanup: PASS. Deleted `branch-immich-immich-app`, branch GitRepository, namespace `immich-immich-app`, temporary `local-path-provisioner`, and temporary `cloudnative-pg`; reconciled development `flux-system` back to `main@sha1:ca80a3e23327198a5d8067e5b255351280c3b97a`.
- Result or exception: PASS. Dev smoke exposed and fixed two issues before production: Talos rejected `/var/mnt/local-path-provisioner` as read-only, so local-path now uses `/var/local-path-provisioner`; Immich cold-start exceeded the default Helm 5m timeout while images and CNPG bootstrap completed, so the HelmRelease now has `timeout: 20m`.

## Documentation Impact

- Updated: `docs/runbooks/immich.md`
- Updated: `docs/runbooks/development-cluster.md`
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
- Automated verifier exception: `verify_branch_deploy.py --app immich --include-cluster-base` could not run because `terraform/development/terraform.tfvars` was unavailable in this worktree; manual Flux smoke was run instead without logging secret values.
- Production live smoke exception: production route smoke remains post-merge/reconcile work.
- Follow-up after merge/reconcile: check Flux `infra-cloudnative-pg`, `infra-local-path-provisioner`, `app-immich`; verify `immich-postgres` readiness; run the synthetic smoke job; confirm Grafana dashboard panels populate from Alloy-scraped Immich metrics.

## Final State

- Final branch: `codex/immich-app`
- Final HEAD: pending final evidence commit
- Commit: local conventional commits created and pushed for implementation plus dev-smoke fixes; final evidence commit pending.
