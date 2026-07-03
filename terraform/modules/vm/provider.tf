
terraform {
  required_providers {
    // https://registry.terraform.io/providers/bpg/proxmox/0.97.1/docs
    proxmox = {
      source  = "bpg/proxmox"
      version = "0.111.0"
    }
    // https://registry.terraform.io/providers/hashicorp/random/3.9.0/docs
    random = {
      source  = "hashicorp/random"
      version = "3.9.0"
    }
  }
}
