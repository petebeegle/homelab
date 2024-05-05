locals {
  nodes = flatten([for node in toset(split(",", var.target_nodes)): [for i in range(2): node]])
}

resource "random_pet" "vm" {
  count = length(local.nodes)
  length   = 2
}

resource "proxmox_vm_qemu" "vm" {
  count = length(local.nodes)

  name = "talos-vm-${random_pet.vm[count.index].id}"

  target_node = local.nodes[count.index]
  iso = "local:iso/${var.iso_name}"

  network {
    model = "virtio"
    bridge = "vmbr0"
  }

  scsihw = "virtio-scsi-single"
  disks {
    scsi {
      scsi0 {
        disk {
          storage      = "local-lvm"
          size         = 32
          backup       = false
        }
      }
    }

  }

  memory = 2048
  cores = 2
}

