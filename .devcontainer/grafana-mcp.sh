#!/usr/bin/env bash
# Wrapper for the Grafana MCP server.
# Ensures the API token is provisioned via Terraform before starting the server.
set -euo pipefail

ENV_FILE=~/.config/grafana/mcp.env
TF_DIR=/workspaces/homelab/terraform/external/grafana

provision_token() {
  terraform -chdir="$TF_DIR" init -input=false >/dev/null
  terraform -chdir="$TF_DIR" apply -auto-approve -input=false >/dev/null

  local token
  token=$(terraform -chdir="$TF_DIR" output -raw mcp_token)

  mkdir -p "$(dirname "$ENV_FILE")"
  echo "export GRAFANA_SERVICE_ACCOUNT_TOKEN=${token}" > "$ENV_FILE"
  chmod 600 "$ENV_FILE"
}

# Re-provision if the env file is missing or the key is empty
if [[ ! -f "$ENV_FILE" ]] || ! grep -q 'GRAFANA_SERVICE_ACCOUNT_TOKEN=.\+' "$ENV_FILE"; then
  provision_token
fi

source "$ENV_FILE"

exec "$HOME/.local/bin/uvx" mcp-grafana
