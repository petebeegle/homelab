<!-- BEGIN_TF_DOCS -->
## Requirements

| Name | Version |
|------|---------|
| <a name="requirement_helm"></a> [helm](#requirement\_helm) | 2.15.0 |
| <a name="requirement_proxmox"></a> [proxmox](#requirement\_proxmox) | 3.0.1-rc3 |
| <a name="requirement_talos"></a> [talos](#requirement\_talos) | 0.6.0-alpha.1 |

## Providers

| Name | Version |
|------|---------|
| <a name="provider_helm"></a> [helm](#provider\_helm) | 2.15.0 |
| <a name="provider_talos"></a> [talos](#provider\_talos) | 0.6.0-alpha.1 |

## Modules

| Name | Source | Version |
|------|--------|---------|
| <a name="module_controlplane_nodes"></a> [controlplane\_nodes](#module\_controlplane\_nodes) | ./modules/node | n/a |
| <a name="module_talos_iso"></a> [talos\_iso](#module\_talos\_iso) | ./modules/talos | n/a |
| <a name="module_worker_nodes"></a> [worker\_nodes](#module\_worker\_nodes) | ./modules/node | n/a |

## Resources

| Name | Type |
|------|------|
| [helm_release.cilium](https://registry.terraform.io/providers/hashicorp/helm/2.15.0/docs/resources/release) | resource |
| [talos_cluster_kubeconfig.this](https://registry.terraform.io/providers/siderolabs/talos/0.6.0-alpha.1/docs/resources/cluster_kubeconfig) | resource |
| [talos_machine_bootstrap.this](https://registry.terraform.io/providers/siderolabs/talos/0.6.0-alpha.1/docs/resources/machine_bootstrap) | resource |
| [talos_machine_configuration_apply.controlplane](https://registry.terraform.io/providers/siderolabs/talos/0.6.0-alpha.1/docs/resources/machine_configuration_apply) | resource |
| [talos_machine_configuration_apply.worker](https://registry.terraform.io/providers/siderolabs/talos/0.6.0-alpha.1/docs/resources/machine_configuration_apply) | resource |
| [talos_machine_secrets.this](https://registry.terraform.io/providers/siderolabs/talos/0.6.0-alpha.1/docs/resources/machine_secrets) | resource |
| [talos_client_configuration.this](https://registry.terraform.io/providers/siderolabs/talos/0.6.0-alpha.1/docs/data-sources/client_configuration) | data source |
| [talos_cluster_health.pre_network](https://registry.terraform.io/providers/siderolabs/talos/0.6.0-alpha.1/docs/data-sources/cluster_health) | data source |
| [talos_cluster_health.this](https://registry.terraform.io/providers/siderolabs/talos/0.6.0-alpha.1/docs/data-sources/cluster_health) | data source |
| [talos_machine_configuration.controlplane](https://registry.terraform.io/providers/siderolabs/talos/0.6.0-alpha.1/docs/data-sources/machine_configuration) | data source |
| [talos_machine_configuration.worker](https://registry.terraform.io/providers/siderolabs/talos/0.6.0-alpha.1/docs/data-sources/machine_configuration) | data source |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_nas_ip"></a> [nas\_ip](#input\_nas\_ip) | IP address of the NAS | `string` | `"192.168.3.3"` | no |
| <a name="input_nas_port"></a> [nas\_port](#input\_nas\_port) | Port to connect to the NAS | `string` | `"2200"` | no |
| <a name="input_nas_user"></a> [nas\_user](#input\_nas\_user) | User to connect to the NAS | `string` | `"ansible"` | no |
| <a name="input_node_data"></a> [node\_data](#input\_node\_data) | n/a | <pre>object({<br/>    controlplanes = map(object({<br/>      node = string<br/>      id   = number<br/>    }))<br/>    workers = map(object({<br/>      node = string<br/>      id   = number<br/>    }))<br/>  })</pre> | <pre>{<br/>  "controlplanes": {<br/>    "192.168.3.60": {<br/>      "id": 102,<br/>      "node": "pve01"<br/>    }<br/>  },<br/>  "workers": {<br/>    "192.168.3.61": {<br/>      "id": 103,<br/>      "node": "pve01"<br/>    },<br/>    "192.168.3.62": {<br/>      "id": 200,<br/>      "node": "pve02"<br/>    }<br/>  }<br/>}</pre> | no |
| <a name="input_pm_api_token_id"></a> [pm\_api\_token\_id](#input\_pm\_api\_token\_id) | n/a | `any` | n/a | yes |
| <a name="input_pm_api_token_secret"></a> [pm\_api\_token\_secret](#input\_pm\_api\_token\_secret) | n/a | `any` | n/a | yes |
| <a name="input_pm_api_url"></a> [pm\_api\_url](#input\_pm\_api\_url) | n/a | `any` | n/a | yes |

## Outputs

| Name | Description |
|------|-------------|
| <a name="output_kubeconfig"></a> [kubeconfig](#output\_kubeconfig) | n/a |
| <a name="output_talosconfig"></a> [talosconfig](#output\_talosconfig) | n/a |
<!-- END_TF_DOCS -->
