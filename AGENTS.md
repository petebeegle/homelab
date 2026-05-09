# AGENTS.md

Kubernetes homelab on Proxmox and Talos OS, managed with Flux GitOps.

Stack: Terraform, Talos OS, Kubernetes, Flux, Cilium, Gateway API, SOPS/Age, Synology NFS, Grafana/Loki/Mimir/Alloy.

## Operating Rules

- Treat Git as the source of truth. Change desired state in this repo, then let Flux reconcile it.
- Keep live-cluster changes temporary unless a runbook explicitly says otherwise.
- Commit only SOPS-encrypted secret manifests. Kubernetes Secret files use repo path names ending with the standard secret manifest filenames matched by `.sops.yaml`.
- Use Gateway API with Cilium for ingress. Prefer `HTTPRoute` or `TLSRoute` resources instead of traditional Kubernetes Ingress resources.
- Use StorageClass `nfs-csi-storage` for persistent app storage unless a decision record supersedes it.
- Manage Talos nodes through `talosctl`; Talos nodes do not support SSH.
- Preserve other people's work. Check the working tree before editing and avoid unrelated rewrites.

## Tool Routing

| Tool | Use for |
| --- | --- |
| Kubernetes API or Kubernetes MCP | Resource CRUD, pods, logs, events, Flux CRDs, HelmRelease and Kustomization status |
| Grafana API or Grafana MCP | Metrics, logs, dashboards, alert rules, datasource checks |
| CLI | Fallback when an API/MCP cannot provide computed debug output |

For metrics queries, use Grafana with PromQL or LogQL. For crashing pods, inspect Kubernetes pod status and logs.

Useful CLI fallbacks:

```bash
flux debug kustomization <name> --show-vars
flux debug helmrelease <name> -n <namespace> --show-values
sops secret.yaml
kubectl create job --from=cronjob.batch/renovate renovate-manual-run -n renovate
```

## Context Management

- Compact or summarize at stable checkpoints: after research, after a milestone, or after a debugging session.
- Avoid compaction in the middle of an implementation because summaries can drop exact names, paths, and values.
- Clear context between unrelated tasks rather than carrying stale assumptions forward.
- When resuming, start by reading `AGENTS.md`, `PLANS.md`, `docs/architecture.md`, and the relevant files under `docs/decisions/` or `docs/runbooks/`.

## Architecture

Generated relationship map:

- `docs/architecture.md` is generated from Kubernetes and Terraform source files.
- Do not edit it by hand. Run `python3 tools/architecture/render.py --write`, then commit the result.
- Pre-commit runs `python3 tools/architecture/render.py --check` and fails if it is stale.

Flux cluster entrypoint:

- `kubernetes/clusters/production/kustomization.yaml` applies `kubernetes/clusters/production/cluster-vars.yaml`, `flux-system/`, `infra/`, and `apps/`.
- Cluster-specific Flux Kustomizations live in `kubernetes/clusters/production/infra/` and `kubernetes/clusters/production/apps/`.
- Shared manifests live in `kubernetes/infra/` and `kubernetes/apps/`.
- Flux variable substitution comes from the `cluster-vars` ConfigMap in `flux-system`.

Primary dependency chain:

1. `crds`: Gateway API, snapshotter, monitoring CRDs.
2. `cert-manager`, `nfs-csi`, `grafana-operator`: depend on CRDs.
3. `cilium`: depends on CRDs.
4. `certs`: depends on cert-manager and Cilium.
5. `gateway`: depends on CRDs, Cilium, and certs.
6. `authentik`: SSO/IdP, depends on gateway and cert-manager.
7. `monitoring`, `loki`, `mimir`, `otel-collector`: depend on gateway.
8. `alloy`: depends on Loki and Mimir.
9. `grafana`: depends on gateway, grafana-operator, Loki, and Mimir.
10. Apps: depend on gateway; NFS-backed apps also depend on `nfs-csi`.

## Key Patterns

- Apps live in directories under `kubernetes/apps/` with a local Kustomization file, workload or HelmRelease manifests, optional secret manifests, and optional Gateway routes.
- Apps are activated by Flux Kustomization files under `kubernetes/clusters/production/apps/`, then listed from `kubernetes/clusters/production/apps/kustomization.yaml`.
- Shared manifests use variables such as `${cluster_domain}` and `${nfs_server}`.
- Internal HTTP exposure uses `HTTPRoute` parent `gateway/internal`, section `https-gateway`.
- External TLS passthrough uses `TLSRoute` against the passthrough Gateway for hosts outside the cluster.
- Synology CSI runs in the `dataplane` namespace and must be healthy before PVC-backed workloads can schedule.

## Before Pushing Kubernetes Changes

- Confirm HelmRelease `dependsOn` covers required CRDs, storage, and ingress dependencies.
- Confirm PVCs use `nfs-csi-storage` unless intentionally using another storage class.
- Confirm Gateway routes reference an existing Gateway and section.
- Confirm SOPS files are encrypted before staging.
- After push, confirm Kustomizations, HelmReleases, and nodes are Ready.

## Decision Records And Runbooks

Decision records are in `docs/decisions/`. General operational procedures are in `docs/runbooks/`; Codex-local operator notes are in `.codex/runbooks/`.
