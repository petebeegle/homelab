# AGENTS.md

Kubernetes homelab on Proxmox and Talos OS, managed with Flux GitOps.

Stack: Terraform, Talos OS, Kubernetes, Flux, Cilium, Gateway API, SOPS/Age,
Synology NFS, Grafana/Loki/Mimir/Alloy.

## Start Here

- Use Spec-Driven Development for repository changes. Start with
  `docs/runbooks/spec-driven-development.md`, then keep implementation artifacts
  in `specs/<implementation>/`.
- Use the mandatory implementation workflow in
  `docs/runbooks/implementation-workflow.md`, accepted by
  `docs/decisions/codex-implementation-workflow.md`.
- Binding architecture and operating decisions live in `docs/decisions/`.
  SDD artifacts summarize and trace to them; they do not replace them.
- General operational procedures live in `docs/runbooks/`; Codex-local notes live
  in `.codex/runbooks/`.
- `docs/architecture.md` is generated. Do not edit it by hand; run
  `python3 tools/architecture/render.py --write` when Kubernetes or Terraform
  source changes affect it.

## Critical Invariants

- Treat Git as the source of truth. Change desired state in this repo, then let
  Flux reconcile it.
- Keep live-cluster changes temporary unless a runbook explicitly says
  otherwise. Never make production-first mutations.
- Validate Kubernetes, Terraform, Flux, Gateway, storage, secret reference, and
  app behavior changes through the development cluster before production-oriented
  PR completion, or document the unavailable-infrastructure exception and
  substitute checks.
- Commit only SOPS-encrypted secret manifests. Kubernetes Secret manifests must
  use repo path names matched by `.sops.yaml`.
- Use Gateway API with Cilium for ingress. Use `HTTPRoute` or `TLSRoute`, not
  traditional Kubernetes `Ingress`.
- Use StorageClass `nfs-csi-storage` for persistent app storage unless a binding
  decision record supersedes it.
- Manage Talos nodes through `talosctl`; Talos nodes do not support SSH.
- Preserve other people's work. Check the working tree before editing and avoid
  unrelated rewrites.

## Implementation Ownership

- Break work into named implementations. One implementation maps to one branch,
  one `specs/<implementation>/` directory, and one PR.
- Plan in `/workspaces/homelab`, but make tracked implementation edits only in
  `/workspaces/homelab-ideas/<implementation>` on branch
  `codex/<implementation>`.
- Before tracked edits, create and validate `.codex/tmp/active-implementation`,
  `.codex/tmp/implementation-plan.yaml`,
  `.codex/tmp/implementation-owner-attestation.yaml`, and matching delegation
  token evidence under `.codex/tmp/delegation-tokens/`.
- Before cloning, stage required ignored local secret/config files under
  `.codex/tmp/implementation-secrets/<implementation>/` in the main checkout
  without logging secret contents; install staged files into the same
  repo-relative paths in implementation and verifier clones before commands that
  need them.
- Runtime scratch files stay under `.codex/tmp/` and are not committed. Durable
  requirements, plans, tasks, and evidence stay under `specs/<implementation>/`.
- Do not create verifier approval for your own implementation. A separate
  verifier records `.codex/tmp/verifier-approved` and verifier attestation for
  the exact `HEAD` before PR creation.

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

## Useful Fallback Commands

```bash
flux debug kustomization <name> --show-vars
flux debug helmrelease <name> -n <namespace> --show-values
sops secret.yaml
kubectl create job --from=cronjob.batch/renovate renovate-manual-run -n renovate
python3 tools/architecture/render.py --check
```
