locals {
  jellyfin_igpu_vm_ids = toset([160, 161])

  jellyfin_igpu_pci_maps = [
    {
      comment      = "pve01 Intel iGPU for production worker VMID 160"
      id           = "8086:a780"
      iommu_group  = 0
      node         = "pve01"
      path         = "0000:00:02.0"
      subsystem_id = "1028:0c79"
    },
    {
      comment      = "pve02 Intel iGPU for production worker VMID 161"
      id           = "8086:4680"
      iommu_group  = 0
      node         = "pve02"
      path         = "0000:00:02.0"
      subsystem_id = "1028:0c7b"
    }
  ]

  jellyfin_igpu_pci_passthrough_devices = [
    {
      mapping = proxmox_hardware_mapping_pci.jellyfin_igpu.name
    }
  ]

  node_labels = {
    for node in var.nodes : node.address => merge(
      {
        "homelab.petebeegle.com/proxmox-host" = node.node
        "homelab.petebeegle.com/vm-id"        = tostring(node.vm_id)
        "homelab.petebeegle.com/machine-type" = node.machine_type
      },
      contains(tolist(local.jellyfin_igpu_vm_ids), node.vm_id) ? {
        "homelab.petebeegle.com/jellyfin-igpu" = "true"
      } : {}
    )
  }
}

module "talos_provision" {
  source = "../modules/talos-provision"

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

resource "proxmox_hardware_mapping_pci" "jellyfin_igpu" {
  name             = "jellyfin-igpu"
  comment          = "Production Intel iGPU mapping for Jellyfin hardware transcoding nodes."
  mediated_devices = false
  map              = local.jellyfin_igpu_pci_maps
}

module "kubernetes_nodes" {
  source = "../modules/vm"
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

  pci_passthrough_devices = contains(tolist(local.jellyfin_igpu_vm_ids), each.value.vm_id) ? local.jellyfin_igpu_pci_passthrough_devices : []

  additional_tags = [each.value.machine_type]
}

module "talos_bootstrap" {
  source     = "../modules/talos-bootstrap"
  depends_on = [module.kubernetes_nodes]

  talos_version      = var.talos_version
  kubernetes_version = var.kubernetes_version
  installer          = module.talos_provision.installer_url

  cluster = {
    name     = "k8s-proxmox-cluster"
    endpoint = "https://192.168.30.150:6443"
  }

  control_nodes = [for node in var.nodes : node.address if node.machine_type == "controlplane"]
  worker_nodes  = [for node in var.nodes : node.address if node.machine_type == "worker"]
  node_labels   = local.node_labels

  allow_scheduling_on_control_planes = false
  cilium_operator_replicas           = 3
  kubeconfig_output_path             = var.kubeconfig_output_path
  talosconfig_output_path            = var.talosconfig_output_path

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
    interpreter = ["/usr/bin/env", "bash", "-c"]

    environment = {
      FLUX_BOOTSTRAP_PATH = var.flux_bootstrap_path
      GITHUB_TOKEN        = var.github_token
      GITHUB_USER         = var.github_user
      KUBECONFIG          = pathexpand(var.kubeconfig_output_path)
    }

    command = file("${path.module}/../scripts/flux-install.sh")
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
