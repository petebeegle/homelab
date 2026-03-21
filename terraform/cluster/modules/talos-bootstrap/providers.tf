terraform {
  required_providers {
    // https://registry.terraform.io/providers/siderolabs/talos/0.10.1/docs
    talos = {
      source  = "siderolabs/talos"
      version = "0.10.1"
    }
    // https://registry.terraform.io/providers/hashicorp/helm/3.1.1/docs
    helm = {
      source  = "hashicorp/helm"
      version = "3.1.1"
    }
    // https://registry.terraform.io/providers/hashicorp/local/2.7.0/docs
    local = {
      source  = "hashicorp/local"
      version = "2.7.0"
    }
  }
}
