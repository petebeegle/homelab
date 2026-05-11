
terraform {
  required_providers {
    // https://registry.terraform.io/providers/siderolabs/talos/0.10.1/docs
    talos = {
      source  = "siderolabs/talos"
      version = "0.11.0"
    }
    // https://registry.terraform.io/providers/bpg/proxmox/0.97.1/docs
    proxmox = {
      source  = "bpg/proxmox"
      version = "0.97.1"
    }
  }
}
