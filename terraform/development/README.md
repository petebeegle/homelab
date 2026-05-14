# Development Terraform Root

This root provisions the dedicated single-node development Talos cluster and bootstraps Flux at `./kubernetes/clusters/development`.

Keep local shared credentials in ignored `terraform/development/terraform.tfvars`; the default development node is declared in `variables.tf` so production nodes are not copied by accident.

<!-- BEGIN_TF_DOCS -->
## Requirements

| Name | Version |
| ---- | ------- |
| <a name="requirement_helm"></a> [helm](#requirement\_helm) | 3.1.1 |
| <a name="requirement_kubernetes"></a> [kubernetes](#requirement\_kubernetes) | 3.1.0 |
| <a name="requirement_proxmox"></a> [proxmox](#requirement\_proxmox) | 0.97.1 |

## Providers

| Name | Version |
| ---- | ------- |
| <a name="provider_proxmox"></a> [proxmox](#provider\_proxmox) | 0.97.1 |
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
| [proxmox_virtual_environment_file.talos_iso](https://registry.terraform.io/providers/bpg/proxmox/0.97.1/docs/resources/virtual_environment_file) | resource |
| [terraform_data.bootstrap_script](https://registry.terraform.io/providers/hashicorp/terraform/latest/docs/resources/data) | resource |

## Inputs

| Name | Description | Type | Default | Required |
| ---- | ----------- | ---- | ------- | :------: |
| <a name="input_docker_password"></a> [docker\_password](#input\_docker\_password) | Docker password for authenticating to the pass-through docker registry | `string` | n/a | yes |
| <a name="input_docker_user"></a> [docker\_user](#input\_docker\_user) | Docker user for authenticating to the pass-through docker registry | `string` | n/a | yes |
| <a name="input_flux_bootstrap_path"></a> [flux\_bootstrap\_path](#input\_flux\_bootstrap\_path) | Repository path that Flux should bootstrap for development | `string` | `"./kubernetes/clusters/development"` | no |
| <a name="input_github_token"></a> [github\_token](#input\_github\_token) | GitHub token to use for the bootstrap script | `string` | n/a | yes |
| <a name="input_github_user"></a> [github\_user](#input\_github\_user) | GitHub user to use for the bootstrap script | `string` | n/a | yes |
| <a name="input_kubeconfig_output_path"></a> [kubeconfig\_output\_path](#input\_kubeconfig\_output\_path) | Path where the development kubeconfig should be written | `string` | `"~/.kube/homelab-development.config"` | no |
| <a name="input_nodes"></a> [nodes](#input\_nodes) | List of nodes to create in the development cluster | <pre>list(object({<br/>    address      = string<br/>    node         = string<br/>    vm_id        = number<br/>    memory       = number<br/>    cores        = number<br/>    machine_type = string<br/>    disk_size    = number<br/>  }))</pre> | <pre>[<br/>  {<br/>    "address": "192.168.30.170",<br/>    "cores": 4,<br/>    "disk_size": 180,<br/>    "machine_type": "controlplane",<br/>    "memory": 24576,<br/>    "node": "pve04",<br/>    "vm_id": 170<br/>  }<br/>]</pre> | no |
| <a name="input_pm_api_token_id"></a> [pm\_api\_token\_id](#input\_pm\_api\_token\_id) | n/a | `any` | n/a | yes |
| <a name="input_pm_api_token_secret"></a> [pm\_api\_token\_secret](#input\_pm\_api\_token\_secret) | n/a | `any` | n/a | yes |
| <a name="input_pm_api_url"></a> [pm\_api\_url](#input\_pm\_api\_url) | n/a | `any` | n/a | yes |
| <a name="input_talos_version"></a> [talos\_version](#input\_talos\_version) | The version of Talos to use for the cluster | `string` | n/a | yes |
| <a name="input_talosconfig_output_path"></a> [talosconfig\_output\_path](#input\_talosconfig\_output\_path) | Path where the development talosconfig should be written | `string` | `"~/.talos/homelab-development.config"` | no |

## Outputs

| Name | Description |
| ---- | ----------- |
| <a name="output_kubeconfig"></a> [kubeconfig](#output\_kubeconfig) | n/a |
| <a name="output_talosconfig"></a> [talosconfig](#output\_talosconfig) | n/a |
<!-- END_TF_DOCS -->
