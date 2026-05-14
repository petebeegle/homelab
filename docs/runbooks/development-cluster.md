---
status: current
scope:
  - development-cluster
  - terraform
  - flux
authority: operational
created: 2026-05-14
last_verified: 2026-05-14
---

# Development Cluster

Use this runbook to create, bootstrap, test, and clean up the dedicated development cluster.

## Shape

- Terraform root: `terraform/development`
- Flux entrypoint: `kubernetes/clusters/development`
- Cluster name: `homelab-development`
- Endpoint: `https://192.168.30.170:6443`
- Default node: VM `170` on `pve04`, IP `192.168.30.170`, single schedulable control-plane node, 4 CPU, 24576 MB memory, 180 GB disk
- Domain: `development.lab.petebeegle.com`
- LoadBalancer pools: internal `192.168.30.224/28`, external `192.168.40.224/28`
- Gateway IPs: internal `192.168.30.225`, passthrough `192.168.30.226`, external `192.168.40.225`, external passthrough `192.168.40.226`
- ACME: Let's Encrypt staging through the shared Cloudflare issuer

The development base intentionally includes CRDs, Cilium, cert-manager/certs, Gateway API, NFS CSI, and whoami. Authentik, games/media apps, Cloudflare tunnels, Renovate, VPN, and the full monitoring stack are omitted to keep the single-node cluster resource-conscious and to avoid production-only secrets or traffic paths unless a test explicitly needs them.

## Local Tfvars

Do not commit `terraform/development/terraform.tfvars`; it is ignored by Git.

Start from the shared secret/config values already used by production, but do not copy production `nodes` into development unless you are intentionally overriding the default development VM:

```sh
awk '
BEGIN { skip=0; depth=0 }
/^[[:space:]]*nodes[[:space:]]*=/ {
  skip=1
  depth=gsub(/\[/,"[")-gsub(/\]/,"]")+gsub(/\{/,"{")-gsub(/\}/,"}")
  next
}
skip {
  depth+=gsub(/\[/,"[")-gsub(/\]/,"]")+gsub(/\{/,"{")-gsub(/\}/,"}")
  if (depth<=0) skip=0
  next
}
{ print }
' terraform/production/terraform.tfvars > terraform/development/terraform.tfvars
```

If you override `nodes`, keep the development node unique from production. The default is the single `192.168.30.170` control-plane VM.

## Terraform Apply

```sh
cd terraform/development
terraform init
terraform plan
terraform apply
```

The Talos bootstrap module writes cluster-specific operator files by default:

- kubeconfig: `~/.kube/homelab-development.config`
- talosconfig: `~/.talos/homelab-development.config`

Use them explicitly when inspecting the cluster:

```sh
export KUBECONFIG=~/.kube/homelab-development.config
export TALOSCONFIG=~/.talos/homelab-development.config
```

## Flux Bootstrap

The development Terraform root runs the shared bootstrap script with `FLUX_BOOTSTRAP_PATH=./kubernetes/clusters/development`.

For a manual bootstrap, create the Flux SOPS age Secret first, then point Flux at the development entrypoint:

```sh
kubectl create secret generic sops-age \
  --namespace=flux-system \
  --from-file=keys.agekey="$HOME/.config/sops/age/keys.agekey" \
  --dry-run=client -o yaml | kubectl apply -f -

flux bootstrap github \
  --owner="$GITHUB_USER" \
  --repository=homelab \
  --branch=main \
  --path=./kubernetes/clusters/development \
  --personal
```

After bootstrap, check the base:

```sh
flux get kustomizations
kubectl get nodes -o wide
kubectl get gateway -n gateway
kubectl get httproute -A
```

## Branch Environments

Branch environments are for app-scoped validation on the development cluster. Use `branch_slug` for all uniqueness and route hostnames:

```text
<app>-${branch_slug}.development.lab.petebeegle.com
```

The initial template is in `kubernetes/clusters/development/branches/`, and the first branch-aware app overlay is `kubernetes/apps/whoami/branch/`. The template is not referenced from the live development entrypoint and is suspended by default. To activate one, copy it into a reviewed cluster-layer path, set the real branch name and slug, and unsuspend both the `GitRepository` and Flux `Kustomization`.

## Cluster-Scoped Testing

Test cluster-scoped changes sequentially on the development base. CRDs, controllers, Gateway API shared objects, storage classes, and other cluster-wide resources should not be tested in parallel branch environments because they share reconciliation and ownership boundaries.

## Cleanup

Remove app branch activations by deleting their cluster-layer Flux manifests and allowing Flux to prune them. Confirm namespaces and PVCs are gone before reusing a `branch_slug`.

To retire the whole development cluster:

```sh
cd terraform/development
terraform destroy
```

Then remove or archive the local operator files if they are no longer needed:

```sh
rm -f ~/.kube/homelab-development.config ~/.talos/homelab-development.config
```
