# CLAUDE.md

Kubernetes homelab on Proxmox/Talos OS managed via GitOps (FluxCD).

**Stack:** Terraform, Talos OS, Kubernetes, FluxCD, Cilium, Gateway API, SOPS/Age

## MCP Tool Priority

| MCP | Use for |
|-----|---------|
| `kubernetes` | K8s CRUD, pod logs, events, CRD/Flux resource queries; pod health in `monitoring` ns |
| `grafana` | Dashboards, metrics (PromQL), logs (LogQL), alert rules, datasource inspection |

Never use `kubernetes` MCP to query metrics — use `grafana` MCP.
Never use `grafana` MCP to check if pods are crashing — use `kubernetes` MCP.

CLI is fallback only when MCP tools can't produce the needed output.

## Context Management

- **`/compact`** at logical boundaries: after research, after milestones, after debugging sessions
- **`/clear`** between unrelated tasks (full reset, not a summary)
- Avoid auto-compact mid-implementation — summaries lose variable names and file paths; prefer manual `/compact` at a stable checkpoint

## Commands

```bash
# Terraform (plan runs automatically before apply)
cd terraform/cluster && terraform apply -auto-approve

# FluxCD — CLI only for computed debug output MCP can't produce
flux debug kustomization <name> --show-vars    # variable substitution values
flux debug helmrelease <name> --show-values    # final merged Helm values

# Secrets
sops secret.yaml   # decrypt and view

# Renovate manual run
kubectl create job --from=cronjob.batch/renovate renovate-manual-run -n renovate
```

## Before Pushing Kubernetes Changes

Hooks handle pre-commit and SOPS encryption checks automatically. Verify manually:
- HelmRelease has correct `dependsOn` if it needs CRDs or storage
- PVCs reference StorageClass `nfs-csi-storage`
- Gateway routes reference an existing Gateway

After pushing, confirm Kustomizations, HelmReleases, and nodes are Ready (kubernetes MCP).

## Architecture

### GitOps Dependency Chain
(Each component is a separate Flux Kustomization in `kubernetes/clusters/production/infra/` and `apps/`)

1. **crds** — Gateway API, Snapshotter
2. **cert-manager** (`cert-manager` ns), **nfs-csi** (`dataplane` ns), **grafana-operator** — depend on crds
3. **cilium** — depends on crds
4. **certs** — depends on cert-manager + cilium
5. **gateway** — depends on crds + cilium + certs
6. **authentik** — SSO/IdP (depends on gateway + cert-manager)
7. **monitoring** (base ns/repos), **loki**, **mimir**, **otel-collector** — depend on gateway
8. **alloy** — depends on loki + mimir
9. **grafana** — depends on gateway + grafana-operator + loki + mimir
10. **apps** — each depends on gateway; NFS apps also depend on nfs-csi

Synology CSI (`dataplane` ns) must be healthy before any PVC workload — CSI failure blocks all dependent pods.

### Key Patterns
- **Secrets:** SOPS-encrypted; `.sops.yaml` matches `secret.yaml` and `grafana-env.yaml`
- **Storage:** StorageClass `nfs-csi-storage` (Synology NFS); Btrfs volumes required for quota
- **Ingress:** Gateway API with Cilium — no traditional Ingress resources
- **Apps:** `kubernetes/apps/<name>/` → `app.yaml` (HelmRelease) + optional `secret.yaml`, `httproute.yaml`; each activated by a Flux Kustomization in `kubernetes/clusters/production/apps/`
- **Variable substitution:** All Flux Kustomizations use `postBuild.substituteFrom` to inject values from the `cluster-vars` ConfigMap in `flux-system`. Shared manifests use `${variable}` syntax (e.g., `${cluster_domain}`, `${nfs_server}`).

### Multi-Environment Support
The repo is structured for multiple environments via Flux variable substitution:

- `kubernetes/clusters/<env>/cluster-vars.yaml` — plaintext ConfigMap with env-specific values (domain, IPs, Let's Encrypt server, cert name)
- `kubernetes/clusters/<env>/kustomization.yaml` — includes `cluster-vars.yaml` so it's applied to the cluster
- Every Flux Kustomization has `postBuild.substituteFrom: [{kind: ConfigMap, name: cluster-vars}]`
- Shared manifests in `kubernetes/infra/` and `kubernetes/apps/` use `${cluster_domain}`, `${nfs_server}`, etc. — no hardcoded env-specific values

To add a new environment (`staging`):
1. Create `kubernetes/clusters/staging/cluster-vars.yaml` with staging-specific values
2. Run `flux bootstrap` pointing at `./kubernetes/clusters/staging`
3. Apply a staging-specific SOPS age key as the `sops-age` Secret in `flux-system`
4. Create `kubernetes/clusters/staging/infra/` and `apps/` with the subset of components to run
5. Use `patches:` in cluster-layer Kustomizations for env-specific sizing (replicas, PV sizes) — no overlay directories needed

## Development Environment

Age key: `~/.config/sops/age/keys.agekey`

### External Terraform Workspaces (`terraform/external/`)

| Workspace | Purpose |
|-----------|---------|
| `grafana/` | `claude-mcp` service account + token; `poststart.sh` exports `GRAFANA_SERVICE_ACCOUNT_TOKEN` |
| `nexus/` | Docker registry user and repo config |
| `synology/` | NAS user and NFS export config |

## graphify

This project has a graphify knowledge graph at graphify-out/.

Rules:
- Before answering architecture or codebase questions, read graphify-out/GRAPH_REPORT.md for god nodes and community structure
- If graphify-out/wiki/index.md exists, navigate it instead of reading raw files
- For cross-module "how does X relate to Y" questions, prefer `graphify query "<question>"`, `graphify path "<A>" "<B>"`, or `graphify explain "<concept>"` over grep — these traverse the graph's EXTRACTED + INFERRED edges instead of scanning files
- After modifying code files, run `graphify update .` to keep the graph current (AST-only, no token cost)
- **Cost awareness:** `query`, `explain`, and `--mode deep` incur tokens. See the cost warning section in the graphify skill for details.
