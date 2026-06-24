# Production Terraform Root

This root provisions the production Talos cluster and bootstraps Flux at `./kubernetes/clusters/production`.

The generated kubeconfig and talosconfig are written to cluster-specific paths by default so production and development operator files do not overwrite each other. Production no longer writes to `~/.kube/config` or `~/.talos/config` unless you override the output path variables; use `KUBECONFIG=~/.kube/homelab-production.config` and `TALOSCONFIG=~/.talos/homelab-production.config` for existing local workflows that expect the active cluster config.

<!-- BEGIN_TF_DOCS -->
## Requirements

| Name | Version |
| ---- | ------- |
| <a name="requirement_helm"></a> [helm](#requirement\_helm) | 3.2.0 |
| <a name="requirement_kubernetes"></a> [kubernetes](#requirement\_kubernetes) | 3.1.0 |
| <a name="requirement_proxmox"></a> [proxmox](#requirement\_proxmox) | 0.111.0 |

## Providers

| Name | Version |
| ---- | ------- |
| <a name="provider_proxmox"></a> [proxmox](#provider\_proxmox) | 0.111.0 |
| <a name="provider_terraform"></a> [terraform](#provider\_terraform) | n/a |

## Modules

| Name | Source | Version |
| ---- | ------ | ------- |
| <a name="module_kubernetes_nodes"></a> [kubernetes\_nodes](#module\_kubernetes\_nodes) | ../modules/vm | n/a |
| <a name="module_talos_bootstrap"></a> [talos\_bootstrap](#module\_talos\_bootstrap) | ../modules/talos-bootstrap | n/a |
| <a name="module_talos_provision"></a> [talos\_provision](#module\_talos\_provision) | ../modules/talos-provision | n/a |

## Resources

| Name | Type |
| ---- | ---- |
| [proxmox_hardware_mapping_pci.jellyfin_igpu](https://registry.terraform.io/providers/bpg/proxmox/0.111.0/docs/resources/hardware_mapping_pci) | resource |
| [proxmox_virtual_environment_file.talos_iso](https://registry.terraform.io/providers/bpg/proxmox/0.111.0/docs/resources/virtual_environment_file) | resource |
| [terraform_data.bootstrap_script](https://registry.terraform.io/providers/hashicorp/terraform/latest/docs/resources/data) | resource |

## Inputs

| Name | Description | Type | Default | Required |
| ---- | ----------- | ---- | ------- | :------: |
| <a name="input_docker_password"></a> [docker\_password](#input\_docker\_password) | Docker password for authenticating to the pass-through docker registry | `string` | n/a | yes |
| <a name="input_docker_user"></a> [docker\_user](#input\_docker\_user) | Docker user for authenticating to the pass-through docker registry | `string` | n/a | yes |
| <a name="input_flux_bootstrap_path"></a> [flux\_bootstrap\_path](#input\_flux\_bootstrap\_path) | Repository path that Flux should bootstrap for production | `string` | `"./kubernetes/clusters/production"` | no |
| <a name="input_github_token"></a> [github\_token](#input\_github\_token) | GitHub token to use for the bootstrap script | `string` | n/a | yes |
| <a name="input_github_user"></a> [github\_user](#input\_github\_user) | GitHub user to use for the bootstrap script | `string` | n/a | yes |
| <a name="input_kubeconfig_output_path"></a> [kubeconfig\_output\_path](#input\_kubeconfig\_output\_path) | Path where the production kubeconfig should be written | `string` | `"~/.kube/homelab-production.config"` | no |
| <a name="input_kubernetes_version"></a> [kubernetes\_version](#input\_kubernetes\_version) | Pins the Talos-generated Kubernetes component images so provider defaults cannot jump ahead of the selected Talos version | `string` | `"v1.35.0"` | no |
| <a name="input_nodes"></a> [nodes](#input\_nodes) | List of nodes to create in the cluster | <pre>list(object({<br/>    address      = string<br/>    node         = string<br/>    vm_id        = number<br/>    memory       = number<br/>    cores        = number<br/>    machine_type = string<br/>    disk_size    = number<br/>  }))</pre> | n/a | yes |
| <a name="input_pm_api_token_id"></a> [pm\_api\_token\_id](#input\_pm\_api\_token\_id) | n/a | `any` | n/a | yes |
| <a name="input_pm_api_token_secret"></a> [pm\_api\_token\_secret](#input\_pm\_api\_token\_secret) | n/a | `any` | n/a | yes |
| <a name="input_pm_api_url"></a> [pm\_api\_url](#input\_pm\_api\_url) | n/a | `any` | n/a | yes |
| <a name="input_talos_version"></a> [talos\_version](#input\_talos\_version) | The version of Talos to use for the cluster | `string` | n/a | yes |
| <a name="input_talosconfig_output_path"></a> [talosconfig\_output\_path](#input\_talosconfig\_output\_path) | Path where the production talosconfig should be written | `string` | `"~/.talos/homelab-production.config"` | no |

## Outputs

| Name | Description |
| ---- | ----------- |
| <a name="output_kubeconfig"></a> [kubeconfig](#output\_kubeconfig) | n/a |
| <a name="output_talosconfig"></a> [talosconfig](#output\_talosconfig) | n/a |
<!-- END_TF_DOCS -->
