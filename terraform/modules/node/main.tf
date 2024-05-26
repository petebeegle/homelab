terraform {
  required_providers {
    proxmox = {
      source  = "Telmate/proxmox"
      version = "3.0.1-rc2"
    }
  }
}

resource "random_pet" "name" {
  count  = var.number_of_instances
  length = 2
}

resource "proxmox_vm_qemu" "vm" {
  count = var.number_of_instances

  name = "k8s-${random_pet.name[count.index].id}"

  target_node = var.target_node
  clone       = var.template_name

  agent   = 1
  vmid    = var.vm_id_prefix + count.index
  os_type = "cloud-init"
  onboot  = true
  cores   = 2
  memory  = 8192

  network {
    model  = "virtio"
    bridge = "vmbr0"
  }

  scsihw = "virtio-scsi-single"
  disks {
    scsi {
      scsi0 {
        disk {
          storage = "local-lvm"
          size    = 32
          backup  = false
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

  ipconfig0 = "ip=192.168.3.${var.vm_id_prefix + count.index}/24,gw=192.168.3.1"
  tags      = "kubernetes"
}
