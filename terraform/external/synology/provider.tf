terraform {
  required_providers {
    synology = {
      source  = "synology-community/synology"
      version = "0.6.11"
    }
    external = {
      source  = "hashicorp/external"
      version = "2.4.0"
    }
  }
}

provider "synology" {
  host       = var.synology.host
  user       = var.synology.user
  password   = var.synology.password
  otp_secret = var.synology.otp_secret
}
