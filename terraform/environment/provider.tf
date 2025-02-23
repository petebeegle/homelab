variable "cloudflare_api_token" {}

terraform {
  required_providers {
    cloudflare = {
      source  = "cloudflare/cloudflare"
      version = "5.1.0"
    }
  }
}

provider "cloudflare" {
  api_token = var.cloudflare_api_token
}
