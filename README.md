# Homelab

## Prerequisites
1. A user provisioned in proxmox
2. An api token provisioned in proxmox
3. NFS for storing our ISO's (`nfs` in proxmox)
4. A Github Personal Access Token (PAT) for authenticating with fluxcd
    - Should be able to read/write the repository
5. An [age](./kubernetes/README.md#creating-secrets) secret stored at `~/.config/sops/age/keys.agekey`

## Quickstart
### 1. Configure terraform
Create a `terraform/terraform.tfvars`:
```tf
pm_api_url="https://proxmox:8006/api2/json"
pm_api_token_id="token-n-smokin"
pm_api_token_secret="secret-secrets-are-no-fun"


github_token = "github_pat_qqq"
github_user = "urnamehere"
```

### 2. Configure external dependencies
The following external dependencies also include terraform modules for easier configuration.
#### Nexus
To set-up Nexus, follow the guide [here](./scripts/NEXUS.md).

### 3. Create the cluster
Create and bootstrap an environment via terraform!
```sh
cd terraform/cluster
terraform init

# live más
terraform apply -auto-approve
```

## Upgrader? I hardly know her!
### 1. Upgrade Talos OS
First, we want to upgrade talos os.
```sh
# get internal-ip addresses of all nodes in the cluster
kubectl get nodes -o wide

# recommended to do this manual, what are we crazy? Get {NODE} from the above list, boss
talosctl upgrade --nodes {NODE} \
      --image ghcr.io/siderolabs/installer:v1.9.1
```
> See: [Upgrading Talos](https://www.talos.dev/latest/talos-guides/upgrading-talos/)

### 2. Upgrade K8s
Once we've upgraded talos, we can upgrade k8s.

First we need to ensure that our talos client matches the talos server version, otherwise the
k8s target versio may not exist. To resolve this, we can simply rebuild our developer environment
without the build cache.

If we rebuilt the developer environment, we may need to re-hydrate our `talosconfig` and `kubeconfig`:
```sh
# live más-er
terraform apply -auto-approve
```

Finally, we can upgrade k8s:

```sh
# verify the client version
talosctl version

# upgrade k8s, only the control plane node is needed
# use --dry-run to see what's up
talosctl --nodes {CONTROL_PLANE_NODE} upgrade-k8s --to 1.32.0
```
> See: [Upgrading K8s](https://www.talos.dev/v1.9/kubernetes-guides/upgrading-kubernetes/)

---

## Kubernetes & Flux Quick Reference

### Directory Structure
```text
kubernetes/
├── apps/           # Application manifests (base configs, overlays)
├── clusters/       # Cluster entrypoints and Flux system
├── infrastructure/ # Networking, storage, controllers, etc.
└── README.md       # (See this root README for usage)
```

### SOPS & Secrets
- We use [SOPS](https://github.com/getsops/sops) and [age](https://github.com/FiloSottile/age) for secret encryption.
- Update `.sops.yaml` to reference your age key fingerprint as needed.

#### Create Flux SOPS Secret
```sh
cat ~/.config/sops/age/keys.agekey | \
  kubectl create secret generic sops-age \
  --namespace=flux-system \
  --from-file=keys.agekey=/dev/stdin
```

#### Encrypt/Decrypt Secrets
```sh
# Encrypt a secret
sops -i -e secret.yaml
# Decrypt a secret
sops secret.yaml
```

### Dependency Management (Renovate)
- Renovate runs as a cronjob in the `renovate` namespace.

Manual run:
```sh
kubectl create job --from=cronjob.batch/renovate renovate-manual-run -n renovate
```

Local dry-run:
```sh
docker run --rm \
  -e LOG_LEVEL="debug" \
  -e RENOVATE_CONFIG="$(cat renovate.json)" \
  renovate/renovate:39.42.4 \
  --token "$TOKEN" \
  --dry-run="true" \
  petebeegle/homelab
```

### Handy Flux & K8s Commands
```sh
# View Flux logs
flux logs -f
# Watch kustomization events
flux get kustomizations --watch
# List Helm releases
kubectl get helmreleases -n kube-system
# List Helm repositories
kubectl get helmrepositories -n kube-system
```


---
## Appendices
Random things that have caused me suffering:
- [Configure NFS With Proxmox](./runbooks/configure_nfs_with_proxmox.md)
- [Cloudflare Tunnels](./runbooks/cloudflare_tunnels.md)
- [Resize a PVC like an idiot](./runbooks/resize_pvc.md)

## Terraform Docs for Nerds
- [Main Module](./terraform/README.md)
    - [Create Node](./terraform/modules/node/README.md)
    - [Talos Image](./terraform/modules/talos/README.md)
