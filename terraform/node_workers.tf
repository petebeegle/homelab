module "worker_nodes" {
  for_each = var.node_data.workers
  source   = "./modules/node"

  ipconfig0    = "ip=${each.key}/24,gw=${local.node_gateway}"
  iso_filename = module.talos_iso.filename
  target_node  = each.value.node
  id           = each.value.id
  memory       = each.value.memory
  cores        = each.value.cores
  pcie_device  = each.value.pcie_device

  file_ready = module.talos_iso.id
}

data "talos_machine_configuration" "worker" {
  cluster_name     = local.cluster_name
  cluster_endpoint = local.cluster_endpoint
  machine_type     = "worker"
  machine_secrets  = talos_machine_secrets.this.machine_secrets
}

resource "talos_machine_configuration_apply" "worker" {
  for_each = var.node_data.workers

  client_configuration        = talos_machine_secrets.this.client_configuration
  machine_configuration_input = data.talos_machine_configuration.worker.machine_configuration
  node                        = each.key
}
