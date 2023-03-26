terraform {
  required_providers {
    cloudflare = {
      source  = "cloudflare/cloudflare"
      version = "4.2.0"
    }
  }
}

provider "cloudflare" {
  api_token = var.api_token
}

resource "cloudflare_record" "lab" {
  zone_id = var.zone_id
  name    = "*.lab"
  value   = "192.168.1.9"
  type    = "A"
  ttl     = 3600
  comment = "Managed by Terraform"
}
