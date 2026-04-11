#!/usr/bin/env bash
# PreToolUse: Bash
#
# Intercepts git commit/push and scans staged files matching SOPS path
# patterns (secret.yaml, grafana-env.yaml) for plaintext content.
# SOPS-encrypted files always contain ENC[ markers; plaintext ones don't.
# Blocks the commit/push via permissionDecision:deny if unencrypted data found.

REPO=$(git rev-parse --show-toplevel 2>/dev/null || echo /workspaces/homelab)

CMD=$(jq -r '.tool_input.command')
echo "$CMD" | grep -qE 'git (commit|push)' || exit 0

UNENCRYPTED=$(git -C "$REPO" diff --cached --name-only \
  | grep -E '(secret\.yaml|grafana-env\.yaml)' \
  | while read -r f; do
      fp="$REPO/$f"
      grep -q 'stringData:' "$fp" && ! grep -q 'ENC\[' "$fp" && echo "$f"
    done)

[ -z "$UNENCRYPTED" ] && exit 0

printf '{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":"Unencrypted secret detected: %s — encrypt with: sops -e -i <file>"}}\n' \
  "$UNENCRYPTED"
