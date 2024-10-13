# Homelab

## Prerequisites
1. an ansible user provisioned in proxmox
2. an api token provisioned in proxmox
3. NFS for storing our ISO's (`truenas-nfs` in proxmox)
    - I used TrueNAS Scale and created a pool called `proxmox-data`, cause I'm not creative at all.

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
terraform apply -auto-approve
```

### 3. Bootstrap flux [optional]
```sh
export GITHUB_USER=petebeegle
export GITHUB_TOKEN=github_pat_token
flux bootstrap github \
    --owner=$GITHUB_USER \
    --repository=homelab \
    --branch=main \
    --path=./kubernetes/clusters/production \
    --personal

```

## Docs for Nerds
- [Main Module](./terraform/README.md)
    - [Create Node](./terraform/modules/node/README.md)
    - [Talos Image](./terraform/modules/talos/README.md)
