#!/usr/bin/env bash
# PostToolUse: Edit|Write
#
# Runs pre-commit on the file Claude just edited. Catches YAML lint,
# trailing whitespace, k8s manifest validation, terraform fmt, etc.
# Non-blocking — output is shown but apply always proceeds.

FILE=$(jq -r '.tool_input.file_path // empty')
[ -z "$FILE" ] && exit 0
pre-commit run --files "$FILE" || true
