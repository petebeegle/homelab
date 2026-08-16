terraform {
  required_providers {
    external = {
      source  = "hashicorp/external"
      version = "2.4.1"
    }
    synology = {
      source  = "synology-community/synology"
      version = "0.6.11"
    }
  }
}
