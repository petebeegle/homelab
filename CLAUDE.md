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
(`kubernetes/clusters/production/infrastructure.yaml` and `apps.yaml`)

1. **crds** — Gateway API, Snapshotter
2. **controllers** — Cert-manager (`cert-manager` ns), Synology CSI (`dataplane` ns)
3. **network** — Cilium, Gateway API, certificates (depends on crds + controllers)
4. **authentik** — SSO/IdP (depends on network + controllers)
5. **monitoring** — Grafana, Loki, Mimir, Alloy (depends on network)
6. **apps** — depends on controllers + network + monitoring

Synology CSI (`dataplane` ns) must be healthy before any PVC workload — CSI failure blocks all dependent pods.

### Key Patterns
- **Secrets:** SOPS-encrypted; `.sops.yaml` matches `secret.yaml` and `grafana-env.yaml`
- **Storage:** StorageClass `nfs-csi-storage` (Synology NFS); Btrfs volumes required for quota
- **Ingress:** Gateway API with Cilium — no traditional Ingress resources
- **Apps:** `kubernetes/apps/base/<name>/` → `app.yaml` (HelmRelease) + optional `secret.yaml`, `httproute.yaml`; activated in `kubernetes/apps/production/kustomization.yaml`

## Development Environment

Age key: `~/.config/sops/age/keys.agekey`

### External Terraform Workspaces (`terraform/external/`)

| Workspace | Purpose |
|-----------|---------|
| `grafana/` | `claude-mcp` service account + token; `poststart.sh` exports `GRAFANA_SERVICE_ACCOUNT_TOKEN` |
| `nexus/` | Docker registry user and repo config |
| `synology/` | NAS user and NFS export config |
