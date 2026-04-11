# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an Infrastructure-as-Code homelab repository managing a Kubernetes cluster running on Proxmox with Talos OS. It uses GitOps (FluxCD) for declarative infrastructure management.

**Key Technologies:** Terraform, Talos OS, Kubernetes, FluxCD, Cilium (CNI), Gateway API, SOPS/Age encryption

## MCP Tool Priority

| MCP | Use for |
|-----|---------|
| `kubernetes` | K8s CRUD, pod logs, Helm, events, CRD queries (including Flux CRDs) |
| `grafana` | Dashboards, metrics queries, alert rules, datasource inspection |

CLI is fallback only when MCP tools don't cover the need.

## Commands

### Terraform (Infrastructure)
```bash
cd terraform/cluster
terraform init
terraform apply -auto-approve
```

**Before applying:**
- [ ] `terraform plan` shows expected changes only
- [ ] No secrets in plain text (use variables or SOPS)
- [ ] Node count maintains etcd quorum (odd number of control planes)
- [ ] NFS host/user variables are set in `terraform.tfvars`

### Linting & Validation
```bash
pre-commit run --all-files          # Run all hooks (yamllint, k8svalidate, terraform_fmt)
```

### FluxCD Operations

Use the `kubernetes` MCP for kustomization/helmrelease status, pod logs, events, and CRD queries. CLI is only needed for computed debug output the MCP can't produce:
```bash
flux debug kustomization <name> --show-vars   # Computed variable substitution values
flux debug helmrelease <name> --show-values   # Final merged Helm values (including valuesFrom)
```

**Before pushing Kubernetes changes:**
- [ ] `pre-commit run --all-files` passes
- [ ] SOPS secrets are encrypted — verify with `sops -d secret.yaml`
- [ ] HelmRelease has correct `dependsOn` if it needs CRDs or storage
- [ ] PVCs reference existing StorageClass (`nfs-csi-storage`)
- [ ] Gateway API routes reference existing Gateway

**After any change — confirm everything settled (use `kubernetes` MCP):**
- [ ] All Kustomizations Ready
- [ ] All HelmReleases Ready
- [ ] All nodes Ready
- [ ] No unexpected pods (ignore Running and Completed)

### Secrets (SOPS/Age)
```bash
sops -i -e secret.yaml              # Encrypt a secret in-place
sops secret.yaml                    # Decrypt and view a secret
```

### Talos/Kubernetes Upgrades
```bash
# Upgrade Talos OS (do each node one at a time)
talosctl upgrade --nodes {NODE} --image ghcr.io/siderolabs/installer:v1.9.1

# Upgrade Kubernetes
talosctl --nodes {CONTROL_PLANE_NODE} upgrade-k8s --to 1.32.0
```

### Renovate (Manual Run)
```bash
kubectl create job --from=cronjob.batch/renovate renovate-manual-run -n renovate
```

## Architecture

### Directory Structure
```
terraform/
├── cluster/              # Main cluster provisioning (Proxmox VMs + Talos)
│   └── modules/
│       ├── talos/        # Talos OS config generation & bootstrap
│       └── proxmox/      # VM provisioning
└── external/             # External services (Nexus, Synology)

kubernetes/
├── clusters/production/  # Flux entrypoint & kustomizations
├── infra/
│   ├── crds/             # Gateway API, Snapshotter CRDs
│   ├── controllers/      # Cert-manager, Synology CSI
│   ├── monitoring/       # Observability (Grafana, Loki, Mimir, Alloy)
│   └── network/          # Cilium, Gateway API configs, VPN
└── apps/
    ├── base/             # Application definitions (pihole, jellyfin, etc.)
    └── production/       # Production overlays
```

### GitOps Dependency Chain
FluxCD applies resources in this order via depends-on relationships:
1. **crds** - CRD installations (Gateway API, Snapshotter)
2. **controllers** - Cert-manager (`cert-manager` ns), Synology CSI (`dataplane` ns)
3. **network** - Cilium, Gateway API, certificates
4. **monitoring** - Observability stack (Grafana, Loki, Mimir, Alloy)
5. **apps** - User applications

**Critical:** Storage (Synology CSI in `dataplane` namespace) must be healthy before apps with PVCs can start. If CSI fails, all dependent workloads will be stuck in Pending.

### Key Patterns
- **Secrets:** Always SOPS-encrypted, matched by `.sops.yaml` path patterns (`secret.yaml`, `grafana-env.yaml`)
- **Storage:** Synology CSI with NFS (`synology-nfs-storage` StorageClass), Btrfs volumes required for quota support
- **Ingress:** Gateway API with Cilium (not traditional Ingress resources)
- **Apps:** Deployed as HelmReleases with Kustomize overlays

## Configuration Files

| File | Purpose |
|------|---------|
| `.sops.yaml` | SOPS encryption rules (encrypts `data`/`stringData` in secret files) |
| `.pre-commit-config.yaml` | Pre-commit hooks for linting |
| `.yamllint.yaml` | YAML linting configuration |
| `renovate.json` | Automated dependency updates |

## Development Environment

Use the devcontainer which includes: kubectl, helm, flux, talosctl, terraform, sops, cilium CLI, and pre-commit.

Age key must be at `~/.config/sops/age/keys.agekey` for secret decryption.

### External Service Terraform Workspaces

`terraform/external/` contains workspaces for provisioning credentials on external services:

| Workspace | Purpose |
|-----------|---------|
| `grafana/` | Creates `claude-mcp` service account + token; `poststart.sh` exports `GRAFANA_SERVICE_ACCOUNT_TOKEN` from its output |
| `nexus/` | Docker registry user and repository config |
| `synology/` | NAS user and NFS export config |

## Skills

Use these skills for common tasks — invoke them with `/skill-name`:

| Skill | When to use |
|-------|-------------|
| `add-app` | Scaffolding a new Kubernetes application (HelmRelease, HTTPRoute, production overlay) |
| `add-secret` | Adding any credentials or sensitive values to an application |
| `diagnose-kustomization` | Flux Kustomization not Ready or blocking downstream resources |
| `diagnose-helmrelease` | Flux HelmRelease stuck, failing to install/upgrade, or app not running |
| `observability` | Working with Grafana, Loki, Mimir, or Alloy |
| `storage` | Debugging Synology CSI PVC issues |
| `networking` | Cilium or Gateway API troubleshooting |
| `talos` | Node management, upgrades, or etcd issues |
