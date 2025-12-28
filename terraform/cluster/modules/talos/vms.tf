module "control_planes" {
  source   = "../proxmox"
  for_each = { for key, value in var.nodes : key => value if value.machine_type == "controlplane" }

  providers = {
    proxmox = proxmox
  }

  ip              = each.key
  iso_filename    = local.image_name
  target_node     = each.value.node
  vm_id           = each.value.vm_id
  memory          = each.value.memory
  cores           = each.value.cores
  disk_size       = each.value.disk_size
  additional_tags = ["controlplane"]
}

module "workers" {
  source   = "../proxmox"
  for_each = { for key, value in var.nodes : key => value if value.machine_type == "worker" }

  providers = {
    proxmox = proxmox
  }

  ip              = each.key
  iso_filename    = local.image_name
  target_node     = each.value.node
  vm_id           = each.value.vm_id
  memory          = each.value.memory
  cores           = each.value.cores
  disk_size       = each.value.disk_size
  additional_tags = ["worker"]
}
