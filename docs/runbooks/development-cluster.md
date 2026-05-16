---
status: current
scope:
  - development-cluster
  - terraform
  - flux
authority: operational
created: 2026-05-14
last_verified: 2026-05-16
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

The Talos bootstrap module intentionally renders Cilium with a Terraform-only values overlay that disables Hubble, Hubble Relay, and Hubble UI. This keeps the inline bootstrap manifest deterministic by avoiding Helm-generated TLS Secrets marked as non-idempotent. Flux later reconciles the full Cilium install from `kubernetes/infra/network/cilium/values.yaml`, including the Hubble settings used by the cluster.

If Terraform bootstrap fails with `/bin/sh: set: Illegal option -o pipefail`, the Flux bootstrap script is being executed by Terraform's default inline `local-exec` shell. The shared `terraform/scripts/flux-install.sh` script is Bash and requires `pipefail`, so the `terraform_data.bootstrap_script` provisioner must set `interpreter = ["/usr/bin/env", "bash", "-c"]`.

The Talos bootstrap module writes cluster-specific operator files by default:

- kubeconfig: `~/.kube/homelab-development.config`
- talosconfig: `~/.talos/homelab-development.config`

Use them explicitly when inspecting the cluster:

```sh
export KUBECONFIG=~/.kube/homelab-development.config
export TALOSCONFIG=~/.talos/homelab-development.config
```

For development checks, source the opt-in shortcuts and use `kd` or `fd` without changing the shell's active `KUBECONFIG`:

```sh
. scripts/kube-aliases.sh
kd get nodes -o wide
fd get kustomizations
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
fd get kustomizations
kd get nodes -o wide
kd get gateway -n gateway
kd get httproute -A
```

## Branch Environments

Branch environments are for app-scoped validation on the development cluster. Use `branch_slug` for all uniqueness and route hostnames:

```text
<app>-${branch_slug}.development.lab.petebeegle.com
```

Use `tools/development/verify_branch_deploy.py` as the canonical path for branch validation. The tool loads JSON smoke profiles from `tools/development/smoke-profiles/`, renders the selected activation template, applies it directly to the development cluster, forces Flux reconciliation, runs profile-specific checks, and then removes the temporary branch Flux resources unless `--keep` is set.

The current automated profiles are `whoami` and `synthetics`. Treat apps without a profile as manual or helper-run evidence for now: use the matrix below, record the exact commands and observations, and document any missing profile instead of adding ad hoc harness behavior.

Activation templates live in `kubernetes/clusters/development/branches/`, and branch-aware app payload overlays live under app directories such as `kubernetes/apps/whoami/branch/` and `kubernetes/apps/synthetics/branch/`. The cluster-layer template creates the Flux `GitRepository` and `Kustomization` that point at a branch; the app overlay is the rendered workload payload that Flux applies after substituting `${branch_slug}`. Templates are not referenced from the live development entrypoint and are suspended by default. The verification tool fills `branch_name` and `branch_slug`, sets both Flux objects to `suspend: false`, and applies the rendered activation temporarily.

### Dev-First Requirement

Run covered cluster-affecting changes through the development cluster before production-oriented PR completion. Covered changes include Kubernetes manifests, Terraform, Flux wiring, Gateway routes, storage, secrets references, branch overlays, and app behavior. Docs-only and purely local tooling changes do not require live development validation unless they alter cluster behavior.

Use the `whoami` branch verifier when the supported profile fits the change. Use manual development smoke evidence for apps without automated profiles. Add `--include-cluster-base` for shared cluster base changes before app acceptance. Production remains GitOps-first; development live validation is evidence, not a substitute for durable repository changes.

If the development cluster, kubeconfig, staged development secrets, or required credentials are unavailable, record `smoke_profile: none` with the blocker, substitute checks, and any follow-up needed. Do not treat an actual development validation failure as an exception; fix the change and rerun validation before production-oriented completion.

### Live App Acceptance

Prerequisites:

- The development cluster exists and the base Flux path is healthy.
- `terraform`, `kubectl`, and `flux` are installed locally.
- The default kubeconfig exists at `~/.kube/homelab-development.config`, or pass `--kubeconfig <path>`.
- The branch named by `--branch` is available on origin. Use `--push` to push the current HEAD to origin as that branch before activation.
- `--slug` is deterministic and DNS-safe: lowercase letters, numbers, and hyphens; starts and ends with an alphanumeric character; and is short enough for `whoami-${branch_slug}` Kubernetes names.

Normal live verification:

```sh
python3 tools/development/verify_branch_deploy.py --app whoami --branch codex/example-change --slug example-change --push
```

Synthetic smoke deployment verification:

```sh
python3 tools/development/verify_branch_deploy.py --app synthetics --branch codex/example-change --slug example-change --push
```

Run Terraform apply first when the development cluster base may need to be created or repaired:

```sh
python3 tools/development/verify_branch_deploy.py --app whoami --branch codex/example-change --slug example-change --push --terraform-apply
```

Include a sequential development base reconcile from the target branch when validating cluster-scoped changes before the branch app test:

```sh
python3 tools/development/verify_branch_deploy.py --app whoami --branch codex/example-change --slug example-change --push --include-cluster-base
```

With `--include-cluster-base`, the tool temporarily points the development `flux-system` GitRepository at `--branch`, reconciles the root `flux-system` Kustomization, re-pins the source to the branch, reconciles `crds`, `cert-manager`, `nfs-csi`, `cilium`, `certs`, `gateway`, and `app-whoami` in order, waits for active pods across the cluster to report Ready, and restores the `flux-system` GitRepository to `main` even when validation fails.

Use a custom kubeconfig:

```sh
python3 tools/development/verify_branch_deploy.py --app whoami --branch codex/example-change --slug example-change --push --kubeconfig ~/.kube/alternate-development.config
```

Keep the branch environment for debugging:

```sh
python3 tools/development/verify_branch_deploy.py --app whoami --branch codex/example-change --slug example-change --push --keep --timeout 20m
```

When `--keep` is not set, cleanup is attempted after activation even if verification fails. Cleanup deletes the branch `Kustomization`, waits for the branch namespace to be pruned, and then deletes the branch `GitRepository`. If `--keep` is set, manually delete the Flux resources and confirm the namespace is gone before reusing the slug:

```sh
kubectl --kubeconfig ~/.kube/homelab-development.config -n flux-system delete kustomization.kustomize.toolkit.fluxcd.io/branch-whoami-example-change
kubectl --kubeconfig ~/.kube/homelab-development.config wait namespace/whoami-example-change --for=delete --timeout=10m
kubectl --kubeconfig ~/.kube/homelab-development.config -n flux-system delete gitrepository.source.toolkit.fluxcd.io/branch-example-change
```

The `whoami` profile proves that the pushed branch can be fetched by Flux, the whoami branch overlay can reconcile on the development cluster, the branch namespace exists, at least one branch app pod is active, active branch app pods report Ready, the Service exists, and the HTTPRoute reports `Accepted` and `ResolvedRefs`. The `synthetics` profile proves the synthetic smoke CronJob deploys suspended, the smoke source ConfigMap contains the expected files, `SMOKE_BASE_DOMAIN` is substituted to the development domain, and a temporary Job can run Playwright test discovery with `npm run test -- --list` without executing route probes. Without `--include-cluster-base`, these profiles do not prove production readiness, cross-app behavior, cluster-scoped changes, public Cloudflare routing, or apps outside the selected profile.

### Touched-App Smoke Matrix

For each implementation that changes app behavior, manifests, Gateway routing, storage, secrets references, or branch overlays, list touched apps in the implementation plan or PR summary and choose one smoke path per app:

| Change type | Minimum development validation evidence |
| --- | --- |
| Branch overlay only | Render the branch overlay locally; when supported, run `verify_branch_deploy.py` for the app profile. |
| Workload, Service, or route | Confirm workload readiness, Service presence, and `HTTPRoute` or `TLSRoute` attachment in a development branch namespace. |
| PVC or storage | Confirm PVC binds with `nfs-csi-storage`, the pod mounts it, and cleanup removes branch PVCs unless retained for debugging. |
| Secret reference | Confirm referenced Secret names render correctly and required staged development secrets exist; do not log secret values. |
| Cluster-scoped base dependency | Run a sequential development base reconcile with `--include-cluster-base`, then run the app smoke if an app is affected. |
| Public or external exposure | Confirm the Gateway route attaches and record any Cloudflare, WireGuard, or out-of-cluster dependency that development cannot fully prove. |

### Smoke Profiles

The target model is a config-driven smoke profile per app. A profile should name the app, branch overlay path, activation template, expected namespace, workloads, Services, routes, PVCs, app-specific probes, cleanup expectations, and any required development-only secret/config prerequisites. Profiles should allow the verifier to choose consistent checks without hard-coding each app into the harness.

Current automated profiles:

- `smoke_profile: whoami` with the exact `verify_branch_deploy.py` command and result.
- `smoke_profile: synthetics` with the exact `verify_branch_deploy.py` command and result. This profile deploys the branch CronJob suspended and validates JavaScript discovery; it does not run route probes.
- `smoke_profile: manual` with commands and observations for the touched app.
- `smoke_profile: none` with the reason, such as docs-only, local-only, unavailable development cluster or credentials, missing app branch overlay that cannot be safely emulated manually, or production-only integration.

An exact-`HEAD` smoke report should include:

- implementation name, app name, branch, branch slug, and exact commit SHA tested;
- smoke profile name or documented exception;
- whether `--push`, `--terraform-apply`, `--include-cluster-base`, or `--keep` was used;
- readiness, route, storage, secret reference, and app-specific probe results that apply to the app;
- cleanup status, including any namespaces, Flux resources, or PVCs intentionally left behind;
- timestamp and kubeconfig or context used, without secret contents.

If a smoke report names a different `HEAD` than the branch under review, treat it as stale. Rerun the smoke, record why rerun was impossible, or explicitly mark the stale report as ignored. Remove or supersede stale local reports before handoff so the verifier does not mistake them for current evidence.

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

## Cluster-Scoped Testing

Test cluster-scoped changes sequentially on the development base. CRDs, controllers, Gateway API shared objects, storage classes, and other cluster-wide resources should not be tested in parallel branch environments because they share reconciliation and ownership boundaries. Use `--include-cluster-base` with the branch verifier when the target branch changes shared development base resources and the branch app acceptance should run after that live base reconcile.

Use `--include-cluster-base` when the implementation changes resources under `kubernetes/clusters/development`, shared CRDs, controller installs, Gateway base objects, Cilium, cert-manager, NFS CSI, Flux dependency ordering, or any app dependency that must exist before a branch overlay can be meaningful. Do not use it for docs-only changes or isolated app overlay edits where the development base from `main` is already sufficient.

## Cleanup

Remove app branch activations by deleting their cluster-layer Flux manifests and allowing Flux to prune them. Confirm namespaces and PVCs are gone before reusing a `branch_slug`.

For kept or failed branch smokes, record cleanup status in the smoke report. Before reusing a slug, delete stale branch `Kustomization` and `GitRepository` objects, wait for the branch namespace to disappear, and check for leftover PVCs or app-owned resources. If cleanup fails, leave the evidence visible to the verifier with the resource names and reason.

To retire the whole development cluster:

```sh
cd terraform/development
terraform destroy
```

Then remove or archive the local operator files if they are no longer needed:

```sh
rm -f ~/.kube/homelab-development.config ~/.talos/homelab-development.config
```
