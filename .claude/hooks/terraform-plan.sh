#!/usr/bin/env bash
# PreToolUse: Bash
#
# Intercepts any Bash call containing "terraform apply" and runs
# terraform plan first, so the diff is visible before changes land.
# Works for all workspaces: terraform/cluster, terraform/external/grafana,
# terraform/external/nexus, terraform/external/synology.
#
# Requires a "cd <dir>" prefix in the command to identify the workspace.
# If no cd is present, emits a warning and skips the plan rather than
# guessing the wrong workspace.

REPO=$(git rev-parse --show-toplevel 2>/dev/null || echo /workspaces/homelab)

CMD=$(jq -r '.tool_input.command')
echo "$CMD" | grep -q 'terraform apply' || exit 0

# Extract directory from "cd <dir>" — handles relative and absolute paths
DIR=$(echo "$CMD" | grep -oP '(?<=cd )\S+' | head -1)

if [ -z "$DIR" ]; then
  echo '{"systemMessage":"terraform-plan hook: no cd <dir> found in command — cannot determine workspace, skipping auto-plan. Prefix with: cd terraform/cluster (or external/<workspace>)"}'
  exit 0
fi

# Resolve relative paths against repo root
[[ "$DIR" = /* ]] || DIR="$REPO/$DIR"

if [ ! -d "$DIR" ]; then
  echo "terraform-plan hook: directory $DIR not found, skipping plan" >&2
  exit 0
fi

cd "$DIR"
terraform plan
