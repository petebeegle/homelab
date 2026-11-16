# Homelab

Two Kubernetes clusters (production and development) on Proxmox and Talos OS,
managed with Terraform and Flux. Everything is changed through pull requests.

- **[docs/overview.md](./docs/overview.md)**: how the pieces fit together, with diagrams and a runbook index. Start here.
- [docs/decisions.md](./docs/decisions.md): why it is built this way.
- [docs/troubleshooting.md](./docs/troubleshooting.md): symptom-to-fix tables.
- [AGENTS.md](./AGENTS.md): the rules for agents working in this repo.

## Prerequisites
1. A user provisioned in proxmox
2. An api token provisioned in proxmox
3. NFS for storing our ISO's (`nfs` in proxmox)
4. A Github Personal Access Token (PAT) for authenticating with fluxcd
    - Should be able to read/write the repository
5. An [age](https://github.com/FiloSottile/age) key at `~/.config/sops/age/keys.agekey`, used to decrypt committed secrets (see [Add Secret](./docs/runbooks/add-secret.md))

## Quickstart
### 1. Configure terraform
Create a `terraform/production/terraform.tfvars`:
```tf
pm_api_url="https://proxmox:8006/api2/json"
pm_api_token_id="token-n-smokin"
pm_api_token_secret="secret-secrets-are-no-fun"


github_token = "github_pat_qqq"
github_user = "urnamehere"
```

For the development cluster, copy the shared non-node values into `terraform/development/terraform.tfvars`. Keep `nodes` out of the development tfvars unless you intentionally override the single-node default documented in [Development Cluster](./docs/runbooks/development-cluster.md).

Terraform roots assume their ignored `terraform.tfvars` files contain local credentials and any site-specific overrides. If a tfvars file is missing, create it from your local secret source; do not commit these files.

### 2. Configure external dependencies
The following external dependencies also include terraform modules for easier configuration.

#### Nexus
To set-up Nexus, follow the guide [here](./scripts/NEXUS.md).

#### Grafana
Provision a scoped service account for tooling (MCP, scripts, etc.):
```sh
cd terraform/external/grafana
terraform init
terraform apply
```
This creates an `agent-service-account` Viewer service account in Grafana and outputs a token. The devcontainer's `poststart.sh` exports it automatically as `GRAFANA_SERVICE_ACCOUNT_TOKEN`.

### 3. Create the cluster
Create and bootstrap production via terraform!
```sh
cd terraform/production
terraform init

# live más
terraform apply -auto-approve
```

Create and bootstrap development with the same shared secrets/config, but from the development root:

```sh
cd terraform/development
terraform init
terraform apply
```

## Upgrading

Talos OS and Kubernetes upgrades follow [Upgrade Talos](./docs/runbooks/upgrade-talos.md).

## Working in the repo

Install the git hooks once:

```sh
pre-commit install --hook-type pre-commit --hook-type commit-msg
```

Then follow the [Change Workflow](./docs/runbooks/change-workflow.md): branch, pull request, checks, merge. Do not commit to `main`.

Terraform writes operator config to `~/.kube/homelab-production.config` and `~/.talos/homelab-production.config` (and the `development` equivalents) instead of overwriting `~/.kube/config`. For shortcuts that do not change the shell's active `KUBECONFIG`, source the helper (the devcontainer does this for you):

```sh
. scripts/kube-aliases.sh
kd get nodes   # development cluster
kp get nodes   # production cluster
fd get kustomizations   # flux against development; fp for production
```

Agent tooling runs inside the devcontainer. MCP servers are configured in `.mcp.json` (general clients) and `.codex/config.toml` (Codex). The Grafana token is injected at container start from the `terraform/external/grafana` output; none is committed.

## More

- [Proxmox No-Subscription Repository](./docs/runbooks/proxmox-no-subscription-repository.md)
- [Configure NFS With Proxmox](./docs/runbooks/configure-nfs-with-proxmox.md)
- [Cloudflare Tunnels](./docs/runbooks/cloudflare-tunnels.md)
- [Resize a PVC](./docs/runbooks/resize-pvc.md)
- Terraform module docs: [production](./terraform/production/README.md), [development](./terraform/development/README.md), [VM](./terraform/modules/vm/README.md), [Talos bootstrap](./terraform/modules/talos-bootstrap/README.md), [Talos provision](./terraform/modules/talos-provision/README.md)
