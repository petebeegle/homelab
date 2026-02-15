# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an Infrastructure-as-Code homelab repository managing a Kubernetes cluster running on Proxmox with Talos OS. It uses GitOps (FluxCD) for declarative infrastructure management.

**Key Technologies:** Terraform, Talos OS, Kubernetes, FluxCD, Cilium (CNI), Gateway API, SOPS/Age encryption

## Commands

### Terraform (Infrastructure)
```bash
cd terraform/cluster
terraform init
terraform apply -auto-approve
```

### Linting & Validation
```bash
pre-commit run --all-files          # Run all hooks (yamllint, k8svalidate, terraform_fmt)
```

### FluxCD Operations

**Prefer `homelab-mcp` tools** over CLI commands when available:
- `cluster_health` - aggregated overview of nodes, flux, pods, helmreleases, PVCs
- `flux_status` - kustomization/helmrelease status (replaces `flux get`)
- `flux_logs` - flux controller logs filtered by level (replaces `flux logs`)
- `flux_reconcile` - trigger reconciliation (replaces `flux reconcile`)
- `helmrelease_debug` - deep dive on a HelmRelease with conditions, events, values
- `pod_logs` - pod logs by name, label, or deployment (replaces `kubectl logs`)
- `talos_nodes` - Talos node status with service health
- `talos_logs` - Talos service logs

Fall back to CLI only when MCP tools don't cover the need:
```bash
flux debug kustomization <name> --show-vars   # Inspect variable values
flux debug helmrelease <name> --show-values   # Inspect final Helm values
```

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
