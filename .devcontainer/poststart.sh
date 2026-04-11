#!/usr/bin/env bash
set -euo pipefail

# Extract terraform output to a file with restricted permissions
tf_output_to_file() {
  local dir="$1"
  local output_key="$2"
  local output_file="$3"

  mkdir -p "$(dirname "$output_file")"
  if terraform -chdir="$dir" output -raw "$output_key" > "$output_file" 2>/dev/null; then
    chmod 600 "$output_file"
    return 0
  fi
  return 1
}

# Kubeconfig from Terraform output
tf_output_to_file "terraform/cluster" "kubeconfig" ~/.kube/config

# Grafana MCP token
if tf_output_to_file "terraform/external/grafana" "mcp_token" ~/.config/grafana/mcp.env.tmp; then
  echo "export GRAFANA_SERVICE_ACCOUNT_TOKEN=$(cat ~/.config/grafana/mcp.env.tmp)" > ~/.config/grafana/mcp.env
  chmod 600 ~/.config/grafana/mcp.env
  rm ~/.config/grafana/mcp.env.tmp
fi
