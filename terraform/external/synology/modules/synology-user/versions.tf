terraform {
  required_providers {
    external = {
      source  = "hashicorp/external"
      version = "2.3.5"
    }
    synology = {
      source  = "synology-community/synology"
      version = "0.6.11"
    }
  }
}
