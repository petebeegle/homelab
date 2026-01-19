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
```bash
flux logs -f                        # View Flux reconciliation logs
flux get kustomizations --watch     # Watch kustomization status
kubectl get helmreleases -A         # List all Helm releases
flux logs --level=error             # Show only errors
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

---

## Research Guidance

When investigating new tools or solving problems, use these resources in order:

### Talos Linux
1. **Official docs:** https://www.talos.dev/latest/
2. **Troubleshooting:** https://www.talos.dev/v1.10/introduction/troubleshooting/
3. **GitHub issues:** https://github.com/siderolabs/talos/issues
4. **Key constraint:** No SSH - all management via `talosctl` API

### FluxCD
1. **Official docs:** https://fluxcd.io/flux/
2. **Troubleshooting:** `flux check`, `flux logs --level=error`
3. **GitHub discussions:** https://github.com/fluxcd/flux2/discussions
4. **Dependency ordering:** https://github.com/fluxcd/flux2/discussions/2276

### Cilium & Gateway API
1. **Cilium docs:** https://docs.cilium.io/en/stable/
2. **Gateway API support:** https://docs.cilium.io/en/stable/network/servicemesh/gateway-api/gateway-api/
3. **Key setting:** `kubeProxyReplacement: true` required for Gateway API

### Observability Stack (Grafana, Loki, Mimir, Alloy)
1. **Grafana docs:** https://grafana.com/docs/
2. **Loki setup:** https://grafana.com/docs/loki/latest/setup/
3. **Mimir setup:** https://grafana.com/docs/mimir/latest/
4. **Alloy (collector):** https://grafana.com/docs/alloy/latest/
5. **Recommended:** Use Kubernetes Monitoring Helm chart for unified setup

### Synology CSI
1. **GitHub:** https://github.com/SynologyOpenSource/synology-csi
2. **Requirements:** DSM 7.0+, Btrfs volume (ext4 lacks quota support)
3. **Protocol:** NFS v4.1 recommended for multi-pod access (RWX)

---

## Troubleshooting

### Talos Nodes

**No SSH access** - Use `talosctl` for all operations:
```bash
# Check service status
talosctl -n <NODE_IP> service etcd
talosctl -n <NODE_IP> service kubelet

# View logs
talosctl -n <NODE_IP> logs kubelet
talosctl -n <NODE_IP> logs controller-runtime

# Check etcd health (control plane only)
talosctl -n <NODE_IP> etcd members

# Verify images are available
talosctl -n <NODE_IP> image ls --namespace system
```

**Troubleshooting order:** Always start with kube-apiserver, which requires healthy etcd. Check etcd → kubelet → controller-runtime.

**Common issues:**
- Certificate IP errors: Check for subnet conflicts with 10.244.0.0/16 (pods) or 10.96.0.0/12 (services)
- Never use VIP as Talos API endpoint
- Worker nodes cannot forward API requests - always use control plane IPs

### FluxCD Reconciliation

```bash
# Check overall health
flux check

# View all resources and their status
flux get all -A

# Identify failing kustomizations
flux get kustomizations

# Check specific HelmRelease
flux get helmrelease <name> -n <namespace>
kubectl describe helmrelease <name> -n <namespace>

# Force reconciliation
flux reconcile kustomization <name> --with-source
flux reconcile helmrelease <name> -n <namespace>
```

**Common issues:**
- "Cannot create empty commit": Already bootstrapped on same branch/path
- HelmRelease stuck: Check `kubectl describe` for Helm errors, often CRD ordering issues
- Source not ready: Check GitRepository or HelmRepository status

### Synology CSI / Storage

```bash
# Check CSI driver pods (namespace is 'dataplane')
kubectl get pods -n dataplane

# Check StorageClass
kubectl get storageclass

# Check PVC status
kubectl get pvc -A

# Describe stuck PVC
kubectl describe pvc <name> -n <namespace>

# Check CSI driver logs
kubectl logs -n dataplane -l app.kubernetes.io/name=synology-csi
```

**Common issues:**
- "Couldn't find any host available": Subfolder bug in some versions - CSI volumes must be at volume root
- PVC stuck Pending: Check NFS export permissions, ensure CIDR covers all worker node IPs
- Mount failures: Verify NFS v4.1 connectivity from nodes to NAS (192.168.30.99)
- UID/GID mismatch: Container user doesn't match NFS export permissions

**NFS export requirements:**
- Allow your homelab VLAN (192.168.30.0/24)
- Allow devcontainer subnet (172.17.0.0/16) if developing locally
- Use Btrfs volumes for quota/shared folder support

### Cilium & Gateway API

```bash
# Check Cilium status
cilium status

# Check Gateway resources
kubectl get gateways -A
kubectl get httproutes -A
kubectl get tlsroutes -A

# Check Cilium logs
kubectl logs -n kube-system -l k8s-app=cilium

# Verify connectivity
cilium connectivity test
```

**Common issues:**
- Gateway not getting IP: Check `l2announcements.enabled: true` in Cilium config
- TLS not working: Verify cert-manager certificates are Ready
- Source IP not preserved: Cilium handles this automatically, no `externalTrafficPolicy` needed

### Observability Stack

```bash
# Check all monitoring pods
kubectl get pods -n monitoring

# Grafana logs
kubectl logs -n monitoring -l app.kubernetes.io/name=grafana

# Loki logs
kubectl logs -n monitoring -l app.kubernetes.io/name=loki

# Mimir logs
kubectl logs -n monitoring -l app.kubernetes.io/name=mimir

# Alloy (collector) logs
kubectl logs -n monitoring -l app.kubernetes.io/name=alloy
```

**Common issues:**
- Mimir OOM: Increase limits, reduce initial metric burst on restart
- Loki ingestion errors: Check storage backend (minio) connectivity
- No metrics in Grafana: Verify Alloy is scraping targets, check discovery config
- Alloy not forwarding: Check `config.alloy` for correct endpoint URLs

---

## Validation Checklists

### Before Applying Terraform Changes
- [ ] `terraform plan` shows expected changes only
- [ ] No secrets in plain text (use variables or SOPS)
- [ ] Node count maintains etcd quorum (odd number of control planes)
- [ ] NFS host/user variables are set in `terraform.tfvars`

### Before Applying Kubernetes Changes
- [ ] `pre-commit run --all-files` passes
- [ ] SOPS secrets are encrypted (`sops -d` to verify they decrypt)
- [ ] HelmRelease has correct `dependsOn` if it needs CRDs or storage
- [ ] PVCs reference existing StorageClass (`synology-nfs-storage`)
- [ ] Gateway API routes reference existing Gateway

### Before Upgrading Talos
- [ ] Backup etcd: `talosctl -n <CP_NODE> etcd snapshot /tmp/etcd.snapshot`
- [ ] Check current version: `talosctl version`
- [ ] Review Talos release notes for breaking changes
- [ ] Upgrade one node at a time, verify cluster health between nodes

### Before Upgrading Kubernetes
- [ ] Talos version supports target K8s version
- [ ] Check deprecated APIs in current manifests
- [ ] Review K8s release notes for breaking changes
- [ ] Use `--dry-run` first: `talosctl upgrade-k8s --to X.Y.Z --dry-run`

### After Any Change
- [ ] `flux get kustomizations` shows all Ready
- [ ] `kubectl get nodes` shows all Ready
- [ ] `kubectl get pods -A` shows no CrashLoopBackOff or Pending
- [ ] Applications are accessible via Gateway

---

## Implementation Patterns

### Adding a New Application

1. Create base config in `kubernetes/apps/base/<app-name>/`
2. Required files:
   - `kustomization.yaml` - lists resources
   - `namespace.yaml` - dedicated namespace
   - `helmrelease.yaml` - HelmRelease with repository reference
   - `helmrepository.yaml` - if new Helm repo needed
3. Add overlay in `kubernetes/apps/production/`
4. Add to `kubernetes/clusters/production/apps.yaml` kustomization
5. If app needs storage, ensure `dependsOn` includes controllers kustomization

### Adding SOPS-Encrypted Secrets

1. Create `secret.yaml` with plain values
2. Encrypt: `sops -i -e secret.yaml`
3. Reference in kustomization.yaml
4. Flux will auto-decrypt using the `sops-age` secret

### Exposing a Service via Gateway API

1. Ensure service exists and has correct port
2. Create HTTPRoute or TLSRoute referencing the Gateway in `kubernetes/infra/network/`
3. For TLS, create Certificate resource referencing cert-manager ClusterIssuer
4. Verify: `kubectl get httproute <name> -o yaml` shows attached to Gateway

### Adding External Service Access

For services outside the cluster (like Proxmox, UniFi):
1. Create ExternalName Service or Endpoints + Service
2. Create TLSRoute with `passthrough` for TLS passthrough
3. See `kubernetes/apps/base/external/` for examples

---

## Common Pitfalls

1. **Changing CNI after deployment** - Major disruption, avoid if possible
2. **Using VIP as Talos API endpoint** - Will fail, use control plane node IPs
3. **Forgetting SOPS encryption** - Secrets will fail to apply, always encrypt
4. **Missing dependsOn** - Apps may try to start before CRDs/storage exist
5. **ext4 volumes with Synology CSI** - Use Btrfs for quota support
6. **Subfolders in Synology CSI volumes** - Known bug, create at volume root
7. **NFS exports missing node IPs** - PVCs will hang in Pending
8. **Helm CRD ordering** - Separate CRD installation into `crds` kustomization
