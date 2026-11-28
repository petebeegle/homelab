terraform {
  # State lives in the NAS S3 gateway (docs/decisions.md, "Terraform state lives in S3 on the NAS").
  # Keys come from AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY: docs/runbooks/terraform-state.md.
  backend "s3" {
    bucket                      = "terraform-state"
    key                         = "external/grafana/terraform.tfstate"
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
    grafana = {
      source  = "grafana/grafana"
      version = "4.36.2"
    }
  }
}

provider "grafana" {
  url  = var.grafana.url
  auth = var.grafana.auth
}
