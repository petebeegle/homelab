terraform {
  required_providers {
    talos = {
      source  = "siderolabs/talos"
      version = "0.8.1"
    }
    proxmox = {
      source  = "Telmate/proxmox"
      version = "3.0.1-rc3"
    }
    helm = {
      source  = "hashicorp/helm"
      version = "2.17.0"
    }
  }
}
