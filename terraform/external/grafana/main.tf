resource "grafana_service_account" "mcp" {
  name = var.service_account_name
  role = "Viewer"
}

resource "grafana_service_account_token" "mcp" {
  name               = "${var.service_account_name}-token"
  service_account_id = grafana_service_account.mcp.id
}

output "mcp_token" {
  value     = grafana_service_account_token.mcp.key
  sensitive = true
}
