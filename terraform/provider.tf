variable "pm_api_url" {}
variable "pm_api_token_id" {}
variable "pm_api_token_secret" {}
variable "github_pat" {}

locals {
  github_owner      = split("/", var.github_slug)[0]
  github_repository = split("/", var.github_slug)[1]
}

terraform {
  required_providers {
    talos = {
      source  = "siderolabs/talos"
      version = "0.6.0"
    }
    proxmox = {
      source  = "Telmate/proxmox"
      version = "3.0.1-rc3"
    }
    flux = {
      source  = "fluxcd/flux"
      version = "1.4.0"
    }
    github = {
      source  = "integrations/github"
      version = "6.3.0"
    }
    helm = {
      source  = "hashicorp/helm"
      version = "2.15.0"
    }
  }
}

provider "proxmox" {
  pm_tls_insecure     = true
  pm_api_url          = var.pm_api_url
  pm_api_token_id     = var.pm_api_token_id
  pm_api_token_secret = var.pm_api_token_secret
}

provider "flux" {
  kubernetes = {
    config_path = "~/.kube/config"
  }
  git = {
    url = "https://github.com/${var.github_slug}.git"
    http = {
      username = "git"
      password = var.github_pat
    }
  }
}

provider "github" {
  token = var.github_pat
  owner = local.github_owner
}

provider "helm" {
  kubernetes {
    config_path = "~/.kube/config"
  }

}
