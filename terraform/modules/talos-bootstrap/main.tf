locals {
  all_nodes = setunion(var.worker_nodes, var.control_nodes)
}

resource "talos_machine_secrets" "this" {
  talos_version = var.talos_version
}

data "talos_client_configuration" "this" {
  cluster_name         = var.cluster.name
  client_configuration = talos_machine_secrets.this.client_configuration

  nodes     = local.all_nodes
  endpoints = var.control_nodes
}

resource "talos_machine_bootstrap" "this" {
  depends_on = [
    talos_machine_configuration_apply.control_plane_apply,
    talos_machine_configuration_apply.worker_apply
  ]

  client_configuration = talos_machine_secrets.this.client_configuration
  node                 = tolist(var.control_nodes)[0]
  endpoint             = tolist(var.control_nodes)[0]
}

data "talos_cluster_health" "this" {
  depends_on = [
    talos_machine_configuration_apply.control_plane_apply,
    talos_machine_configuration_apply.worker_apply,
    talos_machine_bootstrap.this
  ]

  skip_kubernetes_checks = false
  client_configuration   = data.talos_client_configuration.this.client_configuration
  control_plane_nodes    = var.control_nodes
  worker_nodes           = var.worker_nodes
  endpoints              = data.talos_client_configuration.this.endpoints

  timeouts = {
    read = "10m"
  }
}

resource "talos_cluster_kubeconfig" "this" {
  depends_on           = [talos_machine_bootstrap.this]
  client_configuration = talos_machine_secrets.this.client_configuration
  node                 = tolist(var.control_nodes)[0]
}

resource "local_file" "kube_config" {
  depends_on      = [talos_cluster_kubeconfig.this]
  content         = talos_cluster_kubeconfig.this.kubeconfig_raw
  filename        = pathexpand("~/.kube/config")
  file_permission = "0600"
}

resource "local_file" "talos_config" {
  depends_on = [data.talos_client_configuration.this]

  content         = data.talos_client_configuration.this.talos_config
  filename        = pathexpand("~/.talos/config")
  file_permission = "0600"
}

output "kubeconfig" {
  value     = talos_cluster_kubeconfig.this.kubeconfig_raw
  sensitive = true
}

output "talosconfig" {
  value     = data.talos_client_configuration.this.talos_config
  sensitive = true
}
