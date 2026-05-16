#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(cd -- "$script_dir/../.." && pwd)"

GRAFANA_URL="${GRAFANA_URL:-https://monitoring.lab.petebeegle.com}"

if [[ -z "${GRAFANA_SERVICE_ACCOUNT_TOKEN:-}" ]]; then
  state_path="$repo_root/terraform/external/grafana/terraform.tfstate"
  if ! GRAFANA_SERVICE_ACCOUNT_TOKEN="$(terraform output -state="$state_path" -raw mcp_token 2>/dev/null)"; then
    printf 'ERROR: failed to load Grafana MCP token from Terraform state at %s.\n' "$state_path" >&2
    printf 'Run terraform apply in terraform/external/grafana/ or set GRAFANA_SERVICE_ACCOUNT_TOKEN in the process environment.\n' >&2
    exit 1
  fi

  if [[ -z "$GRAFANA_SERVICE_ACCOUNT_TOKEN" ]]; then
    printf 'ERROR: Grafana MCP token loaded from Terraform state is empty.\n' >&2
    printf 'Run terraform apply in terraform/external/grafana/ or set GRAFANA_SERVICE_ACCOUNT_TOKEN in the process environment.\n' >&2
    exit 1
  fi
fi

export GRAFANA_URL GRAFANA_SERVICE_ACCOUNT_TOKEN
exec uvx mcp-grafana "$@"
