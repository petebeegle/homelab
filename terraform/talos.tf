
locals {
  cluster_name        = "proxmox-k8s-cluster"
  cluster_endpoint    = "https://${local.controlplanes_nodes[0]}:6443"
  controlplanes_nodes = [for k, v in var.node_data.controlplanes : k]

  node_gateway = "192.168.3.1"
}

module "talos_iso" {
  source = "./modules/talos"

  talos_version = "v1.7.5"

  destination_user = var.nas_user
  destination_host = var.nas_ip
  destination_port = var.nas_port
}


module "controlplane_nodes" {
  for_each = var.node_data.controlplanes
  source   = "./modules/node"

  ipconfig0    = "ip=${each.key}/24,gw=${local.node_gateway}"
  iso_filename = module.talos_iso.filename
  target_node  = each.value.node
  id           = each.value.id
  memory       = each.value.memory
  cores        = each.value.cores

  file_ready = module.talos_iso.id
}

module "worker_nodes" {
  for_each = var.node_data.workers
  source   = "./modules/node"

  ipconfig0    = "ip=${each.key}/24,gw=${local.node_gateway}"
  iso_filename = module.talos_iso.filename
  target_node  = each.value.node
  id           = each.value.id
  memory       = each.value.memory
  cores        = each.value.cores

  file_ready = module.talos_iso.id
}

resource "talos_machine_secrets" "this" {}
data "talos_client_configuration" "this" {
  cluster_name         = local.cluster_name
  client_configuration = talos_machine_secrets.this.client_configuration
  endpoints            = local.controlplanes_nodes
}

data "talos_machine_configuration" "controlplane" {
  cluster_name     = local.cluster_name
  cluster_endpoint = local.cluster_endpoint
  machine_type     = "controlplane"
  machine_secrets  = talos_machine_secrets.this.machine_secrets
}

data "talos_machine_configuration" "worker" {
  cluster_name     = local.cluster_name
  cluster_endpoint = local.cluster_endpoint
  machine_type     = "worker"
  machine_secrets  = talos_machine_secrets.this.machine_secrets
}

resource "talos_machine_configuration_apply" "controlplane" {
  for_each = var.node_data.controlplanes

  client_configuration        = talos_machine_secrets.this.client_configuration
  machine_configuration_input = data.talos_machine_configuration.controlplane.machine_configuration
  node                        = each.key
  config_patches = [yamlencode({
    cluster = {
      network = {
        cni = {
          name = "none"
        }
      }
      proxy = {
        disabled = true
      }
    }
  })]
}

resource "talos_machine_configuration_apply" "worker" {
  for_each = var.node_data.workers

  client_configuration        = talos_machine_secrets.this.client_configuration
  machine_configuration_input = data.talos_machine_configuration.worker.machine_configuration
  node                        = each.key
}

resource "talos_machine_bootstrap" "this" {
  depends_on = [talos_machine_configuration_apply.controlplane]

  client_configuration = talos_machine_secrets.this.client_configuration
  node                 = local.controlplanes_nodes[0]
}

output "talosconfig" {
  value     = data.talos_client_configuration.this.talos_config
  sensitive = true
}
