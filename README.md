# Homelab

## Prerequisites
1. an ansible user provisioned in proxmox
2. an api token provisioned in proxmox
3. NFS for storing our ISO's (`truenas-nfs` in proxmox)
    - I used TrueNAS Scale and created a pool called `proxmox-data`, cause I'm not creative at all.
4. A Github Personal Access Token (PAT) for authenticating with fluxcd
    - Should be able to read/write the repository
## Quickstart
### 1. Configure terraform
Create a `terraform/terraform.tfvars` using values from your proxmox api token:
```tf
pm_api_url="https://proxmox:8006/api2/json"
pm_api_token_id="token-n-smokin"
pm_api_token_secret="secret-secrets-are-no-fun"
```

### 2. Create the cluster

Create and bootstrap an environment via terraform!
```sh
cd terraform
terraform init

# live más
terraform apply -auto-approve -var="bootstrap_new_cluster=true"
```

### 3. Bootstrap flux
```sh
export GITHUB_USER=you
export GITHUB_TOKEN=github_pat_token
```

Now bootstrap that sucker. You really only need to do this once ever.

```sh
flux bootstrap github \
    --owner=$GITHUB_USER \
    --repository=homelab \
    --branch=main \
    --path=./kubernetes/clusters/production \
    --personal
```

### 4. Secrets

This one is a PITA. When initially bootstrapping a cluster, we need to create a gpg key (or use an existing one) and add it to the cluster as a secret for flux to use for decryption.

We use [sops](https://github.com/getsops/sops) for encryption/decryption.

```shell
# Get your fingerprint
gpg --list-secret-keys ${KEY_NAME}

# Export into a secret
gpg --export-secret-keys --armor ${FINGERPRINT} |
  kubectl create secret generic sops-gpg \
  --namespace=flux-system \
  --from-file=sops.asc=/dev/stdin
```

## Terraform Docs for Nerds
- [Main Module](./terraform/README.md)
    - [Create Node](./terraform/modules/node/README.md)
    - [Talos Image](./terraform/modules/talos/README.md)
- [Flux Info](./kubernetes/README.md)

