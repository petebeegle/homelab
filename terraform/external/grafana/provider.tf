terraform {
  required_providers {
    grafana = {
      source  = "grafana/grafana"
      version = "3.25.9"
    }
  }
}

provider "grafana" {
  url  = var.grafana.url
  auth = var.grafana.auth
}
