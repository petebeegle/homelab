terraform {
  required_providers {
    proxmox = {
      source  = "Telmate/proxmox"
      version = "3.0.1-rc2"
    }
  }
}

locals {
  tags = [
    "talos",
  ]
}

resource "random_pet" "name" {
  length = 2
}

resource "proxmox_vm_qemu" "vm" {
  name = "k8s-${random_pet.name.id}"

  target_node = var.target_node


  agent    = 1
  os_type  = "cloud-init"
  onboot   = true
  cores    = 2
  cpu      = "x86-64-v2-AES"
  memory   = 8192
  boot     = "c"
  bootdisk = "scsi0"

  network {
    model  = "virtio"
    bridge = "vmbr0"
  }

  scsihw = "virtio-scsi-pci"
  disks {
    scsi {
      scsi0 {
        cdrom {
          iso = var.image
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

  sshkeys = <<EOF
  ${var.ssh_key}
  EOF

  ipconfig0 = "ip=${var.ip_config}/24,gw=${var.gateway}"

  desc = <<EOF
    Created At: ${timestamp()}
    Managed By: Terraform
  EOF
  tags = join(",", local.tags)
}



output "name" {
  value       = proxmox_vm_qemu.vm.name
  description = "Name of the created virtual machine"
}

output "id" {
  value       = proxmox_vm_qemu.vm.id
  description = "Id of the created virtual machine"
}

output "ip" {
  value       = proxmox_vm_qemu.vm.default_ipv4_address
  description = "IP address of the created virtual machine"
}
