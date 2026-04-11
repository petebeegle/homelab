variable "grafana" {
  description = "Grafana API connection details"
  type = object({
    url  = string
    auth = string
  })
  sensitive = true
}

variable "service_account_name" {
  description = "Name of the Grafana service account for Claude MCP"
  type        = string
  default     = "claude-mcp"
}
