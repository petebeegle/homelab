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

data "talos_machine_configuration" "controlplane" {
  cluster_name     = local.cluster_name
  cluster_endpoint = local.cluster_endpoint
  machine_type     = "controlplane"
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
      inlineManifests = [
        {
          name     = "cilium"
          contents = data.helm_template.cilium.manifest
        }
      ]
    }
  })]
}
