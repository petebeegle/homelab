# Implementation Patterns & Common Pitfalls

## Adding a New Application

1. Create base config in `kubernetes/apps/base/<app-name>/`
2. Required files:
   - `kustomization.yaml` - lists resources
   - `namespace.yaml` - dedicated namespace
   - `helmrelease.yaml` - HelmRelease with repository reference
   - `helmrepository.yaml` - if new Helm repo needed
3. Add overlay in `kubernetes/apps/production/`
4. Add to `kubernetes/clusters/production/apps.yaml` kustomization
5. If app needs storage, ensure `dependsOn` includes controllers kustomization

## Adding SOPS-Encrypted Secrets

1. Create `secret.yaml` with plain values
2. Encrypt: `sops -i -e secret.yaml`
3. Reference in kustomization.yaml
4. Flux will auto-decrypt using the `sops-age` secret

## Terraform Changes Checklist

- [ ] `terraform plan` shows expected changes only
- [ ] No secrets in plain text (use variables or SOPS)
- [ ] Node count maintains etcd quorum (odd number of control planes)
- [ ] NFS host/user variables are set in `terraform.tfvars`

## Common Pitfalls

1. **Changing CNI after deployment** - Major disruption, avoid if possible
2. **Using VIP as Talos API endpoint** - Will fail, use control plane node IPs
3. **Forgetting SOPS encryption** - Secrets will fail to apply, always encrypt
4. **Missing dependsOn** - Apps may try to start before CRDs/storage exist
5. **ext4 volumes with Synology CSI** - Use Btrfs for quota support
6. **Subfolders in Synology CSI volumes** - Known bug, create at volume root
7. **NFS exports missing node IPs** - PVCs will hang in Pending
8. **Helm CRD ordering** - Separate CRD installation into `crds` kustomization
