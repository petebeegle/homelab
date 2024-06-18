module "pve01" {
  count = length(var.network_config.ips)

  source = "./modules/node"

  target_node = "pve01"
  ssh_key     = var.ssh_key
  ip_config   = tolist(var.network_config.ips)[count.index]
  gateway     = var.network_config.gateway
  image       = var.image
}

output "pve01" {
  value       = module.pve01.*
  description = "Configuration details for virtual machines created in pve01"
}
