#!/usr/bin/env bash
set -euo pipefail

root="$(git rev-parse --show-toplevel)"
cd "$root"

payload="$(cat || true)"

if ! PAYLOAD="$payload" python3 - <<'PY'
import json
import os
import re
import sys

payload = os.environ.get("PAYLOAD", "")
try:
    data = json.loads(payload) if payload.strip() else {}
except json.JSONDecodeError:
    data = {}

texts: list[str] = []

def walk(value: object) -> None:
    if isinstance(value, str):
        texts.append(value)
    elif isinstance(value, dict):
        for nested in value.values():
            walk(nested)
    elif isinstance(value, list):
        for nested in value:
            walk(nested)

walk(data)
text = "\n".join(texts) if texts else payload

change_terms = re.compile(
    r"\b(add|change|commit|create|delete|edit|fix|implement|modify|patch|remove|rename|update|write)\b",
    re.IGNORECASE,
)
repo_terms = re.compile(
    r"\b(AGENTS\.md|branch|code|commit|docs?|file|hook|harness|implementation|repo|script|test|validator|workflow)\b",
    re.IGNORECASE,
)
read_only_terms = re.compile(
    r"\b(explain|inspect|list|read|review|show|summari[sz]e)\b",
    re.IGNORECASE,
)
negative_change_terms = re.compile(
    r"\b(?:do not|don't|dont|never|no)\s+(?:\w+\s+){0,3}?"
    r"(?:add|change|commit|create|delete|edit|fix|implement|modify|patch|remove|rename|update|write)\b"
    r"|\bread[- ]only\b"
    r"|\bwithout\s+(?:editing|changing|modifying|writing|patching|committing)\b",
    re.IGNORECASE,
)

if negative_change_terms.search(text):
    sys.exit(1)
if read_only_terms.search(text) and not re.search(
    r"\b(?:and|then|also)\s+"
    r"(?:add|change|commit|create|delete|edit|fix|implement|modify|patch|remove|rename|update|write)\b",
    text,
    re.IGNORECASE,
):
    sys.exit(1)

if change_terms.search(text) and repo_terms.search(text):
    sys.exit(0)
if change_terms.search(text):
    sys.exit(0)
sys.exit(1)
PY
then
  exit 0
fi

mkdir -p .codex/tmp
{
  printf 'repo_change_intent=true\n'
  printf 'hook=UserPromptSubmit\n'
  printf 'branch=%s\n' "$(git branch --show-current)"
  printf 'head=%s\n' "$(git rev-parse HEAD)"
  printf 'detected_at=%s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
} >.codex/tmp/repo-change-intent

cat <<'EOF'
Spec Kit workflow reminder: tracked repository changes default to a dedicated worktree.

Use:
  git fetch origin
  git worktree add /workspaces/homelab-worktrees/<implementation> -b codex/<implementation> origin/main

Then run the Spec Kit cycle in that worktree: specify -> plan -> tasks -> implement.
Use the current checkout only when explicitly requested or for read-only/planning work.
EOF
