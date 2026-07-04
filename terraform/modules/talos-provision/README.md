<!-- BEGIN_TF_DOCS -->
## Requirements

| Name | Version |
| ---- | ------- |
| <a name="requirement_proxmox"></a> [proxmox](#requirement\_proxmox) | 0.111.0 |
| <a name="requirement_talos"></a> [talos](#requirement\_talos) | 0.11.0 |

## Providers

| Name | Version |
| ---- | ------- |
| <a name="provider_talos"></a> [talos](#provider\_talos) | 0.11.0 |

## Modules

No modules.

## Resources

| Name | Type |
| ---- | ---- |
| [talos_image_factory_schematic.this](https://registry.terraform.io/providers/siderolabs/talos/0.11.0/docs/resources/image_factory_schematic) | resource |
| [talos_image_factory_extensions_versions.this](https://registry.terraform.io/providers/siderolabs/talos/0.11.0/docs/data-sources/image_factory_extensions_versions) | data source |
| [talos_image_factory_urls.this](https://registry.terraform.io/providers/siderolabs/talos/0.11.0/docs/data-sources/image_factory_urls) | data source |

## Inputs

| Name | Description | Type | Default | Required |
| ---- | ----------- | ---- | ------- | :------: |
| <a name="input_talos_version"></a> [talos\_version](#input\_talos\_version) | Talos version to provision | `string` | n/a | yes |

## Outputs

| Name | Description |
| ---- | ----------- |
| <a name="output_image_name"></a> [image\_name](#output\_image\_name) | n/a |
| <a name="output_installer_url"></a> [installer\_url](#output\_installer\_url) | n/a |
| <a name="output_iso_url"></a> [iso\_url](#output\_iso\_url) | n/a |
<!-- END_TF_DOCS -->
