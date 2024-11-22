# Homelab

## Prerequisites
1. A user provisioned in proxmox
2. An api token provisioned in proxmox
3. NFS for storing our ISO's (`truenas-nfs` in proxmox)
    - I used TrueNAS Scale and created a pool called `proxmox-data`, cause I'm not creative at all.
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

### 2. Create the cluster
Create and bootstrap an environment via terraform!
```sh
cd terraform
terraform init

# live más
terraform apply -auto-approve
```
> ℹ️ Terraform will wait until the cluster is healthy before proceeding to bootstrap flux. This may take up to 10 minutes as it configures cilium via a `batch.job`.

## Terraform Docs for Nerds
- [Main Module](./terraform/README.md)
    - [Create Node](./terraform/modules/node/README.md)
    - [Talos Image](./terraform/modules/talos/README.md)
- [Flux Info](./kubernetes/README.md)
