<!-- BEGIN_TF_DOCS -->
## Requirements

| Name | Version |
|------|---------|
| <a name="requirement_proxmox"></a> [proxmox](#requirement\_proxmox) | 3.0.1-rc3 |

## Providers

| Name | Version |
|------|---------|
| <a name="provider_proxmox"></a> [proxmox](#provider\_proxmox) | 3.0.1-rc3 |
| <a name="provider_random"></a> [random](#provider\_random) | n/a |

## Modules

No modules.

## Resources

| Name | Type |
|------|------|
| [proxmox_vm_qemu.vm](https://registry.terraform.io/providers/Telmate/proxmox/3.0.1-rc3/docs/resources/vm_qemu) | resource |
| [random_pet.name](https://registry.terraform.io/providers/hashicorp/random/latest/docs/resources/pet) | resource |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_cores"></a> [cores](#input\_cores) | The number of cores for the VM | `number` | n/a | yes |
| <a name="input_file_ready"></a> [file\_ready](#input\_file\_ready) | The filename of the ISO image to use for the VM | `string` | n/a | yes |
| <a name="input_id"></a> [id](#input\_id) | The ID of the VM | `number` | n/a | yes |
| <a name="input_ipconfig0"></a> [ipconfig0](#input\_ipconfig0) | The IP configuration for the VM | `string` | n/a | yes |
| <a name="input_iso_filename"></a> [iso\_filename](#input\_iso\_filename) | The filename of the ISO image to use for the VM | `string` | n/a | yes |
| <a name="input_memory"></a> [memory](#input\_memory) | The memory size of the VM | `number` | n/a | yes |
| <a name="input_target_node"></a> [target\_node](#input\_target\_node) | The target proxmox node for the VM | `string` | n/a | yes |

## Outputs

No outputs.
<!-- END_TF_DOCS -->