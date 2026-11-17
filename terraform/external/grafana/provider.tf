terraform {
  required_providers {
    grafana = {
      source  = "grafana/grafana"
      version = "4.55.0"
    }
  }
}

provider "grafana" {
  url  = var.grafana.url
  auth = var.grafana.auth
}
