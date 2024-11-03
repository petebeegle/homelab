resource "random_pet" "name" {
  length = 2
}

resource "proxmox_vm_qemu" "vm" {
  name = "k8s-${random_pet.name.id}"

  target_node = var.target_node

  vmid    = var.id
  agent   = 1
  os_type = "cloud-init"
  onboot  = true
  cores   = var.cores
  cpu     = "x86-64-v2-AES"
  memory  = var.memory
  boot    = "order=scsi0;net0"

  network {
    model  = "virtio"
    bridge = "vmbr0"
  }

  scsihw = "virtio-scsi-pci"
  disks {
    scsi {
      scsi0 {
        cdrom {
          iso = "truenas-nfs:iso/${var.iso_filename}"
        }
      }
      scsi1 {
        disk {
          size    = 16
          backup  = false
          storage = "local-lvm"
        }
      }
    }
    ide {
      ide2 {
        cloudinit {
          storage = "local-lvm"
        }
      }
    }
  }

  ipconfig0 = var.ipconfig0

  desc = <<EOF
    Updated At: ${timestamp()}
    Managed By: Terraform
  EOF
  tags = "kubernetes"

  lifecycle {
    ignore_changes = [desc]
  }

  timeouts {
    create = "2m"
    update = "2m"
    delete = "2m"
  }

  depends_on = [var.file_ready]
}
