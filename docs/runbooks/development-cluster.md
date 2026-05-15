---
status: current
scope:
  - development-cluster
  - terraform
  - flux
authority: operational
created: 2026-05-14
last_verified: 2026-05-15
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

Keep `kubernetes_version` at a version supported by `talos_version`. It defaults to `v1.35.0` so Talos machine configuration generation and bootstrap Cilium rendering stay pinned instead of following newer Terraform provider defaults.

## Terraform Apply

Codex may run Terraform and Flux commands against the development cluster for validation and repair. Keep production GitOps-first and do not apply production Terraform for development validation. Any development live change that fixes or validates behavior must still be made durable through tracked repository changes.

```sh
cd terraform/development
terraform init
terraform plan
terraform apply
```

If `terraform apply` fails because Talos rejects a Kubernetes version as too new, check `talos_version` and `kubernetes_version` together before retrying. Do not work around this with live-cluster edits; update the Terraform variables and re-apply through Git.

If Terraform bootstrap fails with `/bin/sh: set: Illegal option -o pipefail`, the Flux bootstrap script is being executed by Terraform's default inline `local-exec` shell. The shared `terraform/scripts/flux-install.sh` script is Bash and requires `pipefail`, so the `terraform_data.bootstrap_script` provisioner must set `interpreter = ["/usr/bin/env", "bash", "-c"]`.

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

The initial activation template is in `kubernetes/clusters/development/branches/`, and the first branch-aware app payload overlay is `kubernetes/apps/whoami/branch/`. The cluster-layer template creates the Flux `GitRepository` and `Kustomization` that point at a branch; the app overlay is the rendered workload payload that Flux applies after substituting `${branch_slug}`. The template is not referenced from the live development entrypoint and is suspended by default. To activate one, copy it into a reviewed cluster-layer path, set the real branch name and slug, and unsuspend both the `GitRepository` and Flux `Kustomization`.

Local manifest verification does not require pushing a branch:

```sh
export branch_slug=example
export cluster_domain=development.lab.petebeegle.com
kubectl kustomize kubernetes/apps/whoami/branch | flux envsubst --strict

kubectl kustomize kubernetes/clusters/development

cp kubernetes/clusters/development/branches/whoami-template.yaml /tmp/whoami-branch.yaml
perl -0pi -e 's/\$\{branch_name\}/my-branch/g; s/\$\{branch_slug\}/example/g' /tmp/whoami-branch.yaml
flux build kustomization branch-whoami-example \
  --path=./kubernetes/apps/whoami/branch \
  --kustomization-file=/tmp/whoami-branch.yaml \
  --dry-run
```

The live branch environment path does require a pushed branch when Flux reconciles it, because the in-cluster `GitRepository` source fetches from GitHub. For local-only experiments, use `kubectl diff --server-side --dry-run=server -k <path>` or `kubectl apply --server-side --dry-run=server -k <path>` against the development cluster instead of unsuspending the branch `GitRepository`.

## Gateway Environment Overlays

The shared gateway base at `kubernetes/infra/network/gateway` must stay environment-neutral: only `${cluster_domain}`, `*.${cluster_domain}`, `${wildcard_cert_name}`, and shared Gateway plumbing belong there. Production-only hostnames, certificates, listeners, and redirects such as Synology, Proxmox, and Unifi belong in additive overlays under `kubernetes/clusters/production/overlays/gateway`. The development cluster points directly at the shared base so local renders do not need deletion patches for production-only Gateway state.

## Future Enhancements

A small helper script or CLI should eventually create and remove branch environments from a branch name and slug. That tool can copy the activation template, fill `branch_name` and `branch_slug`, unsuspend or suspend the Flux resources, and clean up the activation when the branch test is done.

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
