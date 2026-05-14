data "talos_machine_configuration" "control_plane_configuration" {
  for_each         = var.control_nodes
  cluster_name     = var.cluster.name
  cluster_endpoint = var.cluster.endpoint
  talos_version    = var.talos_version
  machine_type     = "controlplane"
  machine_secrets  = talos_machine_secrets.this.machine_secrets
}

resource "talos_machine_configuration_apply" "control_plane_apply" {
  for_each = var.control_nodes

  client_configuration        = talos_machine_secrets.this.client_configuration
  machine_configuration_input = data.talos_machine_configuration.control_plane_configuration[each.key].machine_configuration
  node                        = each.key

  config_patches = [
    templatefile("${path.module}/templates/control_plane.yaml.tftpl", {
      install_image  = var.installer
      cilium_install = data.helm_template.cilium.manifest
    }),
    templatefile("${path.module}/templates/docker_proxy.yaml.tftpl", {
      docker_user     = var.docker_registry.user
      docker_password = var.docker_registry.password
    })
  ]
}
