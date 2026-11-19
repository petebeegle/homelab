variable "pm_api_url" {}
variable "pm_api_token_id" {}
variable "pm_api_token_secret" {}

terraform {
  required_providers {
    // https://registry.terraform.io/providers/bpg/proxmox/0.97.1/docs
    proxmox = {
      source  = "bpg/proxmox"
      version = "0.123.1"
    }
    // https://registry.terraform.io/providers/hashicorp/helm/3.1.1/docs
    helm = {
      source  = "hashicorp/helm"
      version = "3.2.0"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "3.1.0"
    }
    // Used only by ../modules/*, declared here too so Renovate updates this
    // directory's .terraform.lock.hcl when it bumps them (docs/runbooks/renovate.md).
    // Keep the versions equal to the modules' (tools/renovate/tests enforce it).
    talos = {
      source  = "siderolabs/talos"
      version = "0.11.0"
    }
    local = {
      source  = "hashicorp/local"
      version = "2.9.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "3.9.0"
    }
  }
}

provider "proxmox" {
  endpoint  = var.pm_api_url
  api_token = "${var.pm_api_token_id}=${var.pm_api_token_secret}"
  insecure  = true

  ssh {
    agent    = true
    username = "root"
  }
}

provider "helm" {
  kubernetes = {
    config_path = pathexpand(var.kubeconfig_output_path)
  }
}

provider "kubernetes" {
  config_path = pathexpand(var.kubeconfig_output_path)
}
