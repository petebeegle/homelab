variable "nexus" {
  type = object({
    url      = string
    username = string
    password = string
    insecure = optional(bool, true)
  })

}

terraform {
  # State lives in the NAS S3 gateway (docs/decisions.md, "Terraform state lives in S3 on the NAS").
  # Keys come from AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY: docs/runbooks/terraform-state.md.
  backend "s3" {
    bucket                      = "terraform-state"
    key                         = "external/nexus/terraform.tfstate"
    region                      = "us-east-1"
    endpoints                   = { s3 = "https://s3.petebeegle.com" }
    use_path_style              = true
    use_lockfile                = true
    skip_credentials_validation = true
    skip_region_validation      = true
    skip_requesting_account_id  = true
    skip_metadata_api_check     = true
  }

  required_providers {
    nexus = {
      source  = "datadrivers/nexus"
      version = "2.8.0"
    }

    random = {
      source  = "hashicorp/random"
      version = "3.9.0"
    }
  }
}

provider "nexus" {
  insecure = var.nexus.insecure
  password = var.nexus.password
  url      = var.nexus.url
  username = var.nexus.username
}
