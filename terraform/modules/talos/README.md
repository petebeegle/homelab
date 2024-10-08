<!-- BEGIN_TF_DOCS -->
## Requirements

| Name | Version |
|------|---------|
| <a name="requirement_talos"></a> [talos](#requirement\_talos) | 0.6.0 |

## Providers

| Name | Version |
|------|---------|
| <a name="provider_null"></a> [null](#provider\_null) | n/a |
| <a name="provider_talos"></a> [talos](#provider\_talos) | 0.6.0 |

## Modules

No modules.

## Resources

| Name | Type |
|------|------|
| [null_resource.this](https://registry.terraform.io/providers/hashicorp/null/latest/docs/resources/resource) | resource |
| [talos_image_factory_urls.this](https://registry.terraform.io/providers/siderolabs/talos/0.6.0/docs/data-sources/image_factory_urls) | data source |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_destination_host"></a> [destination\_host](#input\_destination\_host) | Host to connect to | `string` | n/a | yes |
| <a name="input_destination_port"></a> [destination\_port](#input\_destination\_port) | Port to connect to | `number` | n/a | yes |
| <a name="input_destination_user"></a> [destination\_user](#input\_destination\_user) | User to connect to the destination host | `string` | n/a | yes |
| <a name="input_talos_version"></a> [talos\_version](#input\_talos\_version) | Talos version to use | `string` | n/a | yes |

## Outputs

| Name | Description |
|------|-------------|
| <a name="output_filename"></a> [filename](#output\_filename) | n/a |
| <a name="output_id"></a> [id](#output\_id) | Id generated when the provisioner is executed. Used as a dependency for other resources. |
<!-- END_TF_DOCS -->