module "control_planes" {
  source = "../proxmox"

  providers = {
    proxmox = proxmox
  }

  for_each = { for key, value in var.nodes : key => value if value.machine_type == "controlplane" }

  ip           = each.key
  iso_filename = local.image_name
  target_node  = each.value.node
  vm_id        = each.value.vm_id
  memory       = each.value.memory
  cores        = each.value.cores
}

module "workers" {
  source = "../proxmox"

  providers = {
    proxmox = proxmox
  }

  for_each = { for key, value in var.nodes : key => value if value.machine_type == "worker" }

  ip           = each.key
  iso_filename = local.image_name
  target_node  = each.value.node
  vm_id        = each.value.vm_id
  memory       = each.value.memory
  cores        = each.value.cores
}
