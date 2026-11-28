# Rebuild and restore

What survives a lost machine or cluster, where it is, and the order to rebuild
from zero. Each step links to the runbook that has the detail.

## What is kept where

| What | Where | Lost if |
|------|-------|---------|
| Desired state: manifests, Terraform, scripts | GitHub `petebeegle/homelab` | GitHub is lost |
| Terraform state, every root | S3 bucket `terraform-state` on the NAS ([Terraform state](./terraform-state.md)) | the NAS is lost (#555) |
| `terraform.tfvars`, every root | 1Password, "Terraform tfvars <root>" in `cluster bootstrap` | 1Password is lost |
| S3 gateway keys | 1Password, "Terraform state S3" in `cluster bootstrap` | 1Password is lost |
| 1Password operator tokens | 1Password, `onepassword-<cluster>-operator` in `cluster bootstrap` ([1Password operator](./onepassword-operator.md)) | 1Password is lost |
| SOPS Age key (production secrets) | `~/.config/sops/age/keys.agekey` on the operator machine | that machine is lost, unless copied elsewhere |
| App data (PVCs) | NFS on the NAS, `/volume2/Homelab/nfs-csi-<namespace>-<pvc>`, `Retain` | the NAS is lost (#555) |
| Talos secrets, kubeconfig, talosconfig | Terraform state (`talos_machine_secrets`), written to `~/.kube` and `~/.talos` on apply | the state is lost |

The NAS is not backed up yet (#555). Losing it loses state, app data and the
image mirror together. Losing the operator machine only costs the SOPS key, if
that has no other copy.

## Rebuild from zero

Do development first wherever a step applies to both clusters, and check it
before touching production.

1. **NAS.** DSM, shares (`docker`, `Homelab`, `Nexus`), Container Manager
   projects `nexus` and `s3`, DNS records, reverse proxies and certificates:
   [SYNOLOGY.md](../../scripts/SYNOLOGY.md) and [NEXUS.md](../../scripts/NEXUS.md).
   Every Talos node pulls images through `docker-registry.petebeegle.com`, so
   Nexus must be up before any cluster.
2. **State bucket.** Restore `/volume2/docker/s3` from backup, or recreate the
   bucket with `tools/terraform/state_bucket.py` and accept that Terraform will
   need imports. Check: `terraform -chdir=terraform/external/synology plan`.
3. **Operator machine.** Clone the repo, `eval "$(op signin)"`, export the S3
   keys, and run `tools/terraform/fetch_tfvars.sh`
   ([Terraform state](./terraform-state.md)). Put the SOPS Age key at
   `~/.config/sops/age/keys.agekey`. Every root should `init` and `plan`.
4. **Proxmox.** Hosts, the no-subscription repository and NFS:
   [Proxmox no-subscription repository](./proxmox-no-subscription-repository.md),
   [Configure NFS with Proxmox](./configure-nfs-with-proxmox.md).
5. **Clusters.** `terraform apply` in `terraform/development`, then
   `terraform/production`. Each apply creates the VMs, installs Talos, writes
   the kubeconfig and talosconfig, installs the bootstrap Secrets and runs
   `flux bootstrap` ([Development cluster](./development-cluster.md#flux-bootstrap),
   [Upgrade Talos](./upgrade-talos.md) for version pins). Development needs
   only the 1Password token; production also needs the SOPS key.
6. **Flux.** Flux reconciles everything else from Git. Watch
   `flux get kustomizations` until all are Ready; the
   [diagnose a Kustomization](./diagnose-kustomization.md) runbook covers SOPS
   and dependency failures.
7. **Data.** PVCs reattach on their own: the NFS folder name comes from the
   namespace and claim name, so a claim recreated by Flux finds its old folder.
   Check one app's data before trusting the rest.
8. **External.** `terraform apply` in `terraform/external/grafana` and
   `terraform/external/nexus` if those services were rebuilt too. A fresh
   Nexus needs its `docker` password to match the nodes' (`docker_password` in
   the production tfvars); see [NEXUS.md](../../scripts/NEXUS.md).
9. **Check the user path.** The production smoke and the public heartbeat
   ([Synthetic smoke tests](./synthetic-smoke-tests.md)) should pass.

## Restore proof

Last proven 2026-11-28 (#486). Run from a fresh clone of `main` with only a
signed-in `op`:

- `tools/terraform/fetch_tfvars.sh` fetched all five roots.
- Every root ran `init` against the bucket, then `plan`:
  - `external/synology` and `external/nexus`: no changes;
  - `development` and `production`: changes pending since their May applies;
  - `external/grafana`: its stored credentials are rejected (401).

Re-run it after changing how state or inputs are kept.
