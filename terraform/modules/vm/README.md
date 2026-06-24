<!-- BEGIN_TF_DOCS -->
## Requirements

| Name | Version |
| ---- | ------- |
| <a name="requirement_proxmox"></a> [proxmox](#requirement\_proxmox) | 0.111.0 |
| <a name="requirement_random"></a> [random](#requirement\_random) | 3.8.1 |

## Providers

| Name | Version |
| ---- | ------- |
| <a name="provider_proxmox"></a> [proxmox](#provider\_proxmox) | 0.111.0 |
| <a name="provider_random"></a> [random](#provider\_random) | 3.8.1 |

## Modules

No modules.

## Resources

| Name | Type |
| ---- | ---- |
| [proxmox_virtual_environment_vm.kubernetes_node](https://registry.terraform.io/providers/bpg/proxmox/0.111.0/docs/resources/virtual_environment_vm) | resource |
| [random_pet.name](https://registry.terraform.io/providers/hashicorp/random/3.8.1/docs/resources/pet) | resource |
| [proxmox_virtual_environment_datastores.this](https://registry.terraform.io/providers/bpg/proxmox/0.111.0/docs/data-sources/virtual_environment_datastores) | data source |

## Inputs

| Name | Description | Type | Default | Required |
| ---- | ----------- | ---- | ------- | :------: |
| <a name="input_additional_tags"></a> [additional\_tags](#input\_additional\_tags) | Additional tags to append to the VM | `list(string)` | `[]` | no |
| <a name="input_boot"></a> [boot](#input\_boot) | Boot configuration for the VM | <pre>object({<br/>    file      = string<br/>    datastore = string<br/>  })</pre> | n/a | yes |
| <a name="input_cpu_cores"></a> [cpu\_cores](#input\_cpu\_cores) | Number of cpu cores to assign to the VM | `number` | n/a | yes |
| <a name="input_disk_size"></a> [disk\_size](#input\_disk\_size) | Size of the boot disk in gigabytes | `number` | `40` | no |
| <a name="input_memory"></a> [memory](#input\_memory) | Amount of dedicated memory (megabytes) to assign to the VM | `number` | n/a | yes |
| <a name="input_network"></a> [network](#input\_network) | Network configuration for the VM | <pre>object({<br/>    address = string<br/>    gateway = string<br/>  })</pre> | n/a | yes |
| <a name="input_pci_passthrough_devices"></a> [pci\_passthrough\_devices](#input\_pci\_passthrough\_devices) | Optional host PCI devices to attach to the VM. Set exactly one of id or mapping for each device. | <pre>list(object({<br/>    id       = optional(string)<br/>    mapping  = optional(string)<br/>    mdev     = optional(string)<br/>    pcie     = optional(bool)<br/>    rom_file = optional(string)<br/>    rombar   = optional(bool)<br/>    xvga     = optional(bool)<br/>  }))</pre> | `[]` | no |
| <a name="input_target_node_name"></a> [target\_node\_name](#input\_target\_node\_name) | Name of the node to create the VM on | `string` | n/a | yes |
| <a name="input_vm_id"></a> [vm\_id](#input\_vm\_id) | Id to assign to the VM | `number` | n/a | yes |

## Outputs

| Name | Description |
| ---- | ----------- |
| <a name="output_ds"></a> [ds](#output\_ds) | n/a |
<!-- END_TF_DOCS -->
