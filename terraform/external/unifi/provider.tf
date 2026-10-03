terraform {
  required_providers {
    unifi = {
      source  = "ubiquiti-community/unifi"
      version = "0.41.25"
    }
  }
}

provider "unifi" {
  api_url        = var.unifi.api_url
  username       = var.unifi.username
  password       = var.unifi.password
  site           = var.unifi.site
  allow_insecure = var.unifi.allow_insecure
}
