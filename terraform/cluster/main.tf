module "talos_provision" {
  source = "./modules/talos-provision"

  talos_version = var.talos_version
}

resource "proxmox_virtual_environment_file" "talos_iso" {
  content_type = "iso"
  datastore_id = "remote-nas"
  node_name    = "pve01"
  source_file {
    path      = module.talos_provision.iso_url
    file_name = module.talos_provision.image_name
  }
}

module "kubernetes_nodes" {
  source = "./modules/vm"
  providers = {
    proxmox = proxmox
  }
  for_each = {
    for index, node in var.nodes :
    node.address => node
  }

  target_node_name = each.value.node
  vm_id            = each.value.vm_id

  boot = {
    datastore = "local-lvm"
    file      = proxmox_virtual_environment_file.talos_iso.id
  }

  network = {
    address = each.value.address
    gateway = "192.168.30.1"
  }

  cpu_cores = each.value.cores
  memory    = each.value.memory
  disk_size = each.value.disk_size

  additional_tags = [each.value.machine_type]
}

module "talos_bootstrap" {
  source     = "./modules/talos-bootstrap"
  depends_on = [module.kubernetes_nodes]

  talos_version = var.talos_version
  installer     = module.talos_provision.installer_url

  cluster = {
    name     = "k8s-proxmox-cluster"
    endpoint = "https://192.168.30.150:6443"
  }

  control_nodes = [for node in var.nodes : node.address if node.machine_type == "controlplane"]
  worker_nodes  = [for node in var.nodes : node.address if node.machine_type == "worker"]

  docker_registry = {
    user     = var.docker_user
    password = var.docker_password
  }
}

output "kubeconfig" {
  value     = module.talos_bootstrap.kubeconfig
  sensitive = true
}

output "talosconfig" {
  value     = module.talos_bootstrap.talosconfig
  sensitive = true
}

resource "terraform_data" "bootstrap_script" {
  depends_on = [module.talos_bootstrap]

  provisioner "local-exec" {
    environment = {
      GITHUB_TOKEN = var.github_token
      GITHUB_USER  = var.github_user
    }

    command = file("${path.module}/scripts/flux-install.sh")
  }
}

# resource "null_resource" "bootstrap_script" {
#   depends_on = [module.talos]

#   provisioner "local-exec" {
#     environment = {
#       GITHUB_TOKEN = var.github_token
#       GITHUB_USER  = var.github_user
#     }

#     command = file("${path.module}/scripts/flux-install.sh")
#   }
# }
