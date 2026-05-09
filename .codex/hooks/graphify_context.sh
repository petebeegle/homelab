#!/usr/bin/env bash
set -euo pipefail

root="$(git rev-parse --show-toplevel)"
cd "$root"

payload="$(cat || true)"
event_name="$(
  PAYLOAD="$payload" python3 - <<'PY'
import json
import os

payload = os.environ.get("PAYLOAD", "")
try:
    data = json.loads(payload) if payload.strip() else {}
except json.JSONDecodeError:
    data = {}
print(data.get("hook_event_name") or data.get("hookEventName") or "")
PY
)"

if [[ "$event_name" == "SessionStart" || -z "$event_name" ]]; then
  if [[ -f graphify-out/GRAPH_REPORT.md ]]; then
    cat <<'JSON'
{"hookSpecificOutput":{"hookEventName":"SessionStart","additionalContext":"graphify: Knowledge graph exists at graphify-out/. For architecture or cross-module questions, read graphify-out/GRAPH_REPORT.md first and prefer graphify query/path/explain over raw grep when relationships matter."}}
JSON
  fi
  exit 0
fi

if [[ "$event_name" != "PostToolUse" ]]; then
  exit 0
fi

mapfile -t changed_files < <(
  git diff --name-only --diff-filter=ACMRTUXB HEAD -- 2>/dev/null |
    grep -Ev '^graphify-out/' |
    sort -u || true
)

if ((${#changed_files[@]} == 0)); then
  exit 0
fi

cat >&2 <<'EOF'
Codex graphify reminder: files changed while a graphify knowledge graph exists.
Do not auto-refresh graphify from hooks; run `graphify update .` deliberately when graph changes should be committed.
EOF
