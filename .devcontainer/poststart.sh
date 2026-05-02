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
GRAFANA_SERVICE_ACCOUNT_TOKEN=$(tfo -state=terraform/external/grafana/terraform.tfstate -raw mcp_token 2>/dev/null || true)
if [[ -z "$GRAFANA_SERVICE_ACCOUNT_TOKEN" ]]; then
  echo "WARNING: GRAFANA_SERVICE_ACCOUNT_TOKEN is empty — run 'terraform apply' in terraform/external/grafana/ to provision the token"
fi
export GRAFANA_SERVICE_ACCOUNT_TOKEN
