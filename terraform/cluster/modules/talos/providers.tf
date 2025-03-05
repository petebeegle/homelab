terraform {
  required_providers {
    talos = {
      source  = "siderolabs/talos"
      version = "0.7.0"
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
