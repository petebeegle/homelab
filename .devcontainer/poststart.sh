#!/usr/bin/env bash
set -euo pipefail

alias_file="${HOME}/.aliases.zsh"
kube_alias_source='[ -f /workspaces/homelab/scripts/kube-aliases.sh ] && . /workspaces/homelab/scripts/kube-aliases.sh'

mkdir -p "$(dirname "$alias_file")"
touch "$alias_file"
if ! grep -Fxq "$kube_alias_source" "$alias_file"; then
  printf '%s\n' "$kube_alias_source" >> "$alias_file"
fi

# Extract terraform output to a file with restricted permissions
tf_output_to_file() {
  local dir="$1"
  local output_key="$2"
  local output_file="$3"
  local tmp_file

  mkdir -p "$(dirname "$output_file")"
  tmp_file="$(mktemp "${output_file}.tmp.XXXXXX")"
  if terraform -chdir="$dir" output -raw "$output_key" > "$tmp_file" 2>/dev/null; then
    chmod 600 "$tmp_file"
    mv "$tmp_file" "$output_file"
    return 0
  fi
  rm -f "$tmp_file"
  return 1
}

# Operator files from Terraform outputs
operator_files=(
  "development|terraform/development|kubeconfig|${HOME}/.kube/homelab-development.config"
  "development|terraform/development|talosconfig|${HOME}/.talos/homelab-development.config"
  "production|terraform/production|kubeconfig|${HOME}/.kube/homelab-production.config"
  "production|terraform/production|talosconfig|${HOME}/.talos/homelab-production.config"
)

for operator_file in "${operator_files[@]}"; do
  IFS='|' read -r environment dir output_key output_file <<< "$operator_file"
  if ! tf_output_to_file "$dir" "$output_key" "$output_file"; then
    echo "WARNING: ${environment} ${output_key} output is unavailable from ${dir}; leaving ${output_file} unchanged"
  fi
done

# Grafana MCP token
GRAFANA_SERVICE_ACCOUNT_TOKEN=$(terraform output -state=terraform/external/grafana/terraform.tfstate -raw mcp_token 2>/dev/null || true)
if [[ -z "$GRAFANA_SERVICE_ACCOUNT_TOKEN" ]]; then
  echo "WARNING: GRAFANA_SERVICE_ACCOUNT_TOKEN is empty — run 'terraform apply' in terraform/external/grafana/ to provision the token"
fi
export GRAFANA_SERVICE_ACCOUNT_TOKEN

# Codex sandbox prerequisite. This should already be present from the
# devcontainer image build, but keep a clear warning if the container was not
# rebuilt after the Dockerfile change.
if ! command -v bwrap >/dev/null 2>&1; then
  echo "WARNING: bubblewrap is missing — rebuild the devcontainer so Codex sandboxing can use bwrap"
fi

# Codex-native agent tooling. Keep installs idempotent so rebuilding the
# devcontainer is predictable and day-to-day starts stay fast.
if ! command -v codex >/dev/null 2>&1; then
  npm install -g @openai/codex
fi

if ! command -v agnix >/dev/null 2>&1 || ! agnix --version >/dev/null 2>&1; then
  npm install -g agnix || true
fi

# The npm package may ship a glibc-linked binary newer than the Ubuntu base
# image supports. Prefer the musl release binary if the npm binary cannot run.
if ! agnix --version >/dev/null 2>&1; then
  mkdir -p "$HOME/.local/bin"
  tmpdir="$(mktemp -d)"
  curl -fsSL \
    "https://github.com/agent-sh/agnix/releases/download/v0.25.0/agnix-x86_64-unknown-linux-musl.tar.gz" \
    -o "$tmpdir/agnix.tar.gz"
  tar -xzf "$tmpdir/agnix.tar.gz" -C "$tmpdir"
  install -m 0755 "$tmpdir/agnix" "$HOME/.local/bin/agnix"
  rm -rf "$tmpdir"
fi
