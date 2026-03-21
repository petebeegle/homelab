locals {
  datastore = data.proxmox_virtual_environment_datastores.this.datastores[0]
}

resource "random_pet" "name" {
  length = 2
}

data "proxmox_virtual_environment_datastores" "this" {
  node_name = var.target_node_name
  filters = {
    id = var.boot.datastore
  }
}

output "ds" {
  value = data.proxmox_virtual_environment_datastores.this.datastores[0].id
}


resource "proxmox_virtual_environment_vm" "kubernetes_node" {
  name        = "k8s-${random_pet.name.id}"
  description = <<EOF
    Updated At: ${timestamp()}
    Managed By: Terraform
  EOF

  node_name = var.target_node_name
  vm_id     = var.vm_id
  agent {
    enabled = true
  }
  stop_on_destroy = true

  cpu {
    cores = var.cpu_cores
    type  = "x86-64-v2-AES"
  }

  memory {
    dedicated = var.memory
    floating  = 0
  }

  cdrom {
    file_id   = var.boot.file
    interface = "ide3"
  }

  disk {
    datastore_id = local.datastore.id
    interface    = "scsi0"
    size         = var.disk_size
  }

  network_device {
    bridge = "vmbr0"
    model  = "virtio"
  }

  initialization {
    datastore_id = local.datastore.id

    ip_config {
      ipv4 {
        address = "${var.network.address}/24"
        gateway = var.network.gateway
      }
    }
  }


  lifecycle {
    ignore_changes = [description, tags]
  }
  tags = concat(["kubernetes"], var.additional_tags)
}
