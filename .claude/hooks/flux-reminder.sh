#!/usr/bin/env bash
# PostToolUse: Bash
#
# Fires after a successful git push and injects a system message reminding
# Claude to verify Flux reconciliation. Flux is async — a successful push
# does not mean the cluster has converged. Always check kustomization and
# helmrelease status before declaring a change done.

CMD=$(jq -r '.tool_input.command')
echo "$CMD" | grep -q 'git push' || exit 0

echo '{"systemMessage":"Pushed. Verify Flux reconciliation via kubernetes MCP: check kustomization + helmrelease status before declaring done."}'
