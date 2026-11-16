# AGENTS.md

Kubernetes homelab on Proxmox and Talos OS, managed with Flux GitOps.

Stack: Terraform, Talos OS, Kubernetes, Flux, Cilium, Gateway API, SOPS/Age,
Synology NFS, Grafana/Loki/Mimir/Alloy.

## Start Here

- Make every change on a branch and merge it through a pull request; never
  commit to `main`. `docs/runbooks/change-workflow.md` is the procedure and
  `docs/decisions/pr-gated-change-workflow.md` (ADR-0016) is the rule behind it.
- `docs/overview.md` explains how the repo fits together and indexes the
  runbooks. Keep it current when the shape of the platform changes.
- Binding architecture and operating decisions live in `docs/decisions/`.
- Operational procedures live in `docs/runbooks/`.
- `docs/architecture.md` is generated. Do not edit it by hand; run
  `python3 tools/architecture/render.py --write` when Kubernetes or Terraform
  source changes affect it.

## Critical Invariants

- Treat Git as the source of truth. Change desired state in this repo, then let
  Flux reconcile it.
- Keep live-cluster changes temporary unless a runbook explicitly says
  otherwise. Never make production-first mutations.
- Prove changes in the development cluster before they reach production. For
  apps with a smoke profile (`prSmoke: true` in
  `tools/development/smoke-profiles/`), the `dev-smoke` PR check does this. For
  every other Kubernetes, Terraform, Flux, Gateway, storage, secret reference, or
  app behavior change, validate in the development cluster yourself and state in
  the PR description what you ran and what it showed, or the
  unavailable-infrastructure exception and the substitute checks.
- Commit only SOPS-encrypted secret manifests. Kubernetes Secret manifests must
  use repo path names matched by `.sops.yaml`.
- Use Gateway API with Cilium for ingress. Use `HTTPRoute` or `TLSRoute`, not
  traditional Kubernetes `Ingress`.
- Use StorageClass `nfs-csi-storage` for persistent app storage unless a binding
  decision record supersedes it.
- Manage Talos nodes through `talosctl`; Talos nodes do not support SSH.
- Preserve other people's work. Check the working tree before editing and avoid
  unrelated rewrites.

## Change Workflow

- One change, one branch, one PR. Default to a dedicated worktree:
  `/workspaces/homelab-worktrees/<name>` on branch `codex/<name>`. Use the
  current checkout only when explicitly requested.
- No per-change process artifacts are required. For work large enough to need a
  written design or plan, put it under `docs/superpowers/specs/` and
  `docs/superpowers/plans/`, and get the human's approval of the design before
  building it.
- Write a failing test before the code wherever the change has testable
  behavior. Before pushing, run
  `python3 tools/verification/verify.py --profile harness` and pre-commit.
- Required PR checks gate the merge. `dev-smoke` deploys and tests changes to
  smoke-profiled apps in the development cluster; for anything it reports as
  "not smoke-tested", the PR description carries your validation statement.
- To smoke-test by hand:
  `python3 tools/development/verify_branch_deploy.py --app <app> --branch <branch> --slug <slug>`
  (add `--browser` for apps with a browser check).
- Before worktree or clone commands that need ignored local secret/config files,
  stage them under `.codex/tmp/implementation-secrets/<name>/` in the main
  checkout without logging secret contents; install staged files into the same
  repo-relative paths in worktrees or clones before commands that need them.
- Runtime scratch files stay under `.codex/tmp/` and are not committed.
- Prefer automated smoke for user-facing, routed, deployed, or operational
  changes. Do not call such work done from render checks, pod readiness, Service
  probes, or route `Accepted=True` alone; verify the exact user path or record
  the unverified layer.

## Tool Routing

- Use Kubernetes API or Kubernetes MCP for resource CRUD, pod logs, events, Flux
  CRDs, HelmRelease status, and Kustomization status.
- Use Grafana API or Grafana MCP for metrics, logs, dashboards, alert rules, and
  datasource checks.
- Use CLI commands as a fallback when the API or MCP cannot provide the computed
  debug output.

## Homelab Patterns

- Production Flux entrypoint: `kubernetes/clusters/production/kustomization.yaml`.
- Development Flux entrypoint: `kubernetes/clusters/development/kustomization.yaml`.
- Shared manifests live in `kubernetes/infra/` and `kubernetes/apps/`.
- Cluster-specific Flux Kustomizations live under
  `kubernetes/clusters/<cluster>/infra/` and
  `kubernetes/clusters/<cluster>/apps/`.
- LAN HTTP routes attach to Gateway `gateway/internal`, section
  `https-gateway`.
- WireGuard service-plane HTTP routes attach to Gateway `gateway/external`,
  section `https-gateway`; this is not internet-public exposure.
- Internet-public HTTP routes enter through Cloudflare Tunnel to
  `gateway/public`, section `http-gateway`, and also need a cloudflared ingress
  rule.
- LAN TLS passthrough uses Gateway `gateway/passthrough`; WireGuard service-plane
  passthrough uses `gateway/external-passthrough`.
- Synology CSI runs in namespace `dataplane` and must be healthy before
  PVC-backed workloads can schedule.
- Branch environments for smoke-tested apps are kustomize overlays on the real
  manifests (`kubernetes/apps/<app>/branch/`). Do not copy manifests into them.

## Useful Fallback Commands

```bash
flux debug kustomization <name> --show-vars
flux debug helmrelease <name> -n <namespace> --show-values
sops secret.yaml
kubectl create job --from=cronjob.batch/renovate renovate-manual-run -n renovate
python3 tools/architecture/render.py --check
```
