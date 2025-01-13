resource "random_pet" "name" {
  length = 2
}

resource "proxmox_vm_qemu" "vm" {
  name = "k8s-${random_pet.name.id}"

  target_node = var.target_node

  vmid     = var.id
  agent    = 1
  os_type  = "cloud-init"
  onboot   = true
  cores    = var.cores
  cpu_type = "x86-64-v2-AES"
  memory   = var.memory
  boot     = "order=scsi0;net0"

  network {
    id     = 0
    model  = "virtio"
    bridge = "vmbr0"
  }

  scsihw = "virtio-scsi-pci"
  disks {
    scsi {
      scsi0 {
        cdrom {
          iso = "nfs:iso/${var.iso_filename}"
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

  machine = var.pcie_device == null ? "pc-i440fx-6.0" : "q35"
  bios    = var.pcie_device == null ? "seabios" : "ovmf"
  dynamic "pcis" {
    for_each = var.pcie_device != null ? [1] : []
    content {
      pci0 {
        mapping {
          pcie        = true
          primary_gpu = true
          rombar      = true
          mapping_id  = var.pcie_device
        }
      }
    }
  }
  dynamic "efidisk" {
    for_each = var.pcie_device != null ? [1] : []
    content {
      storage = "local-lvm"
      efitype = "4m"
    }
  }

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
