variable "nexus" {
  type = object({
    url      = string
    username = string
    password = string
    insecure = optional(bool, true)
  })

}

terraform {
  required_providers {
    nexus = {
      source  = "datadrivers/nexus"
      version = "2.6.0"
    }

    random = {
      source  = "hashicorp/random"
      version = "3.7.2"
    }
  }
}

provider "nexus" {
  insecure = var.nexus.insecure
  password = var.nexus.password
  url      = var.nexus.url
  username = var.nexus.username
}
