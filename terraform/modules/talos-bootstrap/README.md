<!-- BEGIN_TF_DOCS -->
## Requirements

| Name | Version |
| ---- | ------- |
| <a name="requirement_helm"></a> [helm](#requirement\_helm) | 3.1.1 |
| <a name="requirement_local"></a> [local](#requirement\_local) | 2.8.0 |
| <a name="requirement_talos"></a> [talos](#requirement\_talos) | 0.11.0 |

## Providers

| Name | Version |
| ---- | ------- |
| <a name="provider_helm"></a> [helm](#provider\_helm) | 3.1.1 |
| <a name="provider_local"></a> [local](#provider\_local) | 2.8.0 |
| <a name="provider_talos"></a> [talos](#provider\_talos) | 0.11.0 |

## Modules

No modules.

## Resources

| Name | Type |
| ---- | ---- |
| [local_file.kube_config](https://registry.terraform.io/providers/hashicorp/local/2.8.0/docs/resources/file) | resource |
| [local_file.talos_config](https://registry.terraform.io/providers/hashicorp/local/2.8.0/docs/resources/file) | resource |
| [talos_cluster_kubeconfig.this](https://registry.terraform.io/providers/siderolabs/talos/0.11.0/docs/resources/cluster_kubeconfig) | resource |
| [talos_machine_bootstrap.this](https://registry.terraform.io/providers/siderolabs/talos/0.11.0/docs/resources/machine_bootstrap) | resource |
| [talos_machine_configuration_apply.control_plane_apply](https://registry.terraform.io/providers/siderolabs/talos/0.11.0/docs/resources/machine_configuration_apply) | resource |
| [talos_machine_configuration_apply.worker_apply](https://registry.terraform.io/providers/siderolabs/talos/0.11.0/docs/resources/machine_configuration_apply) | resource |
| [talos_machine_secrets.this](https://registry.terraform.io/providers/siderolabs/talos/0.11.0/docs/resources/machine_secrets) | resource |
| [helm_template.cilium](https://registry.terraform.io/providers/hashicorp/helm/3.1.1/docs/data-sources/template) | data source |
| [talos_client_configuration.this](https://registry.terraform.io/providers/siderolabs/talos/0.11.0/docs/data-sources/client_configuration) | data source |
| [talos_cluster_health.this](https://registry.terraform.io/providers/siderolabs/talos/0.11.0/docs/data-sources/cluster_health) | data source |
| [talos_machine_configuration.control_plane_configuration](https://registry.terraform.io/providers/siderolabs/talos/0.11.0/docs/data-sources/machine_configuration) | data source |
| [talos_machine_configuration.workers](https://registry.terraform.io/providers/siderolabs/talos/0.11.0/docs/data-sources/machine_configuration) | data source |

## Inputs

| Name | Description | Type | Default | Required |
| ---- | ----------- | ---- | ------- | :------: |
| <a name="input_allow_scheduling_on_control_planes"></a> [allow\_scheduling\_on\_control\_planes](#input\_allow\_scheduling\_on\_control\_planes) | Allow Kubernetes workloads to schedule on control-plane nodes | `bool` | `false` | no |
| <a name="input_cilium_operator_replicas"></a> [cilium\_operator\_replicas](#input\_cilium\_operator\_replicas) | Concrete Cilium operator replica count to render into bootstrap Helm values | `number` | n/a | yes |
| <a name="input_cluster"></a> [cluster](#input\_cluster) | Information about the cluster to join | <pre>object({<br/>    name     = string<br/>    endpoint = string<br/>  })</pre> | n/a | yes |
| <a name="input_control_nodes"></a> [control\_nodes](#input\_control\_nodes) | List of nodes to compose the cluster control plane | `set(string)` | n/a | yes |
| <a name="input_docker_registry"></a> [docker\_registry](#input\_docker\_registry) | Docker registry credentials | <pre>object({<br/>    user     = string<br/>    password = string<br/>  })</pre> | n/a | yes |
| <a name="input_installer"></a> [installer](#input\_installer) | Installer url to load | `string` | n/a | yes |
| <a name="input_kubeconfig_output_path"></a> [kubeconfig\_output\_path](#input\_kubeconfig\_output\_path) | Optional path where the generated kubeconfig should be written | `string` | `null` | no |
| <a name="input_talos_version"></a> [talos\_version](#input\_talos\_version) | The version of Talos to use for the cluster | `string` | n/a | yes |
| <a name="input_talosconfig_output_path"></a> [talosconfig\_output\_path](#input\_talosconfig\_output\_path) | Optional path where the generated talosconfig should be written | `string` | `null` | no |
| <a name="input_worker_nodes"></a> [worker\_nodes](#input\_worker\_nodes) | List of nodes to compose the cluster worker plane | `set(string)` | n/a | yes |

## Outputs

| Name | Description |
| ---- | ----------- |
| <a name="output_kubeconfig"></a> [kubeconfig](#output\_kubeconfig) | n/a |
| <a name="output_talosconfig"></a> [talosconfig](#output\_talosconfig) | n/a |
<!-- END_TF_DOCS -->
