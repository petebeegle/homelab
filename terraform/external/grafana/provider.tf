terraform {
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
