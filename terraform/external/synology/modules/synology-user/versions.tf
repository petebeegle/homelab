terraform {
  required_providers {
    external = {
      source  = "hashicorp/external"
      version = "~> 2.0"
    }
    synology = {
      source  = "synology-community/synology"
      version = "~> 0.6"
    }
  }
}
