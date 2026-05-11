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
- All repository code changes must use the mandatory implementation workflow in `docs/runbooks/implementation-workflow.md`, as accepted by `docs/decisions/codex-implementation-workflow.md`, no questions asked.
- Break work into named implementations before editing. Each implementation maps to one PR and may contain multiple conventional commits.
- Use implementation and verifier subagents by default whenever runtime tooling exposes them. This is a standing opt-out preference, so do not ask whether to use subagents for normal implementation or verifier roles; respect explicit task instructions such as "do not use subagents."
- Self-implementation or self-verification is acceptable only when subagent tooling is unavailable or higher-priority runtime policy blocks delegation. Record any fallback to self-verification in `.codex/tmp/pr-summary.md`.
- Every implementation must consider documentation impact. Update stale docs, generated docs, decision records, runbooks, or agent guidance when behavior changes; otherwise record why no docs changed.
- Before cloning, the planner must stage any required ignored local secret/config files into `.codex/tmp/implementation-secrets/<implementation>/`, preserving their repo-relative paths and never logging secret contents.
- Implementation agents must clone `https://github.com/petebeegle/homelab.git` into `/workspaces/homelab-ideas/<implementation>`, create `codex/<implementation>` from `origin/main`, and work only in that sibling clone.
- Before changing tracked files, implementation agents must record `.codex/tmp/active-implementation` with `implementation`, `branch`, `base`, `role`, `clone_path`, `owner_role`, and `owner_agent`; `tools/codex-harness/validate_active_implementation.py` is the enforcement source for marker validity.
- Before changing tracked files, implementation agents must record `.codex/tmp/implementation-plan.yaml`; `tools/codex-harness/validate_implementation_plan.py` is the enforcement source for plan validity.
- Multiple helper agents may contribute to one implementation clone only through the single integrator model: helpers may research, test, verify, or prepare patch recommendations, but one implementation owner owns tracked-file edits, commits, `.codex/tmp/active-implementation`, `.codex/tmp/implementation-plan.yaml`, `.codex/tmp/pr-summary.md`, and final branch state.
- Implementation and verifier agents must install staged secret/config files into identical repo-relative locations in their sibling clones before running commands that need them.
- Before PR creation, record plan-derived PR text in `.codex/tmp/pr-summary.md` so the automatic PR body includes the implementation summary, important changes from the plan, and a documentation impact note listing docs updated/generated or explaining why none were needed.
- After verifier sign-off for the exact `HEAD`, create the PR without intervention, then delete the sibling clone only after PR creation succeeds.

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
- When Kubernetes or Terraform source changes make the architecture check fail, refresh `docs/architecture.md` with `python3 tools/architecture/render.py --write` as part of the same implementation.

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
