module "pve01" {
  source = "./modules/node"

  number_of_instances = var.number_of_instances
  vm_id_prefix        = 200
  target_node         = "pve01"
  ssh_key             = var.ssh_key
  template_name       = var.template_name
}
