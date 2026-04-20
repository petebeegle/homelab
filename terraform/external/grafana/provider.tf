terraform {
  required_providers {
    grafana = {
      source  = "grafana/grafana"
      version = "4.31.3"
    }
  }
}

provider "grafana" {
  url  = var.grafana.url
  auth = var.grafana.auth
}
