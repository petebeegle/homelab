#!/usr/bin/env bash
set -euo pipefail

root="$(git rev-parse --show-toplevel)"
cd "$root"

payload="$(cat || true)"
state_file=".codex/tmp/implementation-workflow-guard-state"
branch="$(git branch --show-current)"

if [[ "${1:-}" == "--record" ]]; then
  mkdir -p .codex/tmp
  {
    printf 'branch=%s\n' "$branch"
    printf 'head=%s\n' "$(git rev-parse HEAD)"
  } >"$state_file"
  exit 0
fi

fail() {
  {
    printf 'Spec Kit workflow guard: refusing tracked-file changes outside an active Spec Kit branch.\n'
    printf '%s\n' "$1"
    printf '\nRequired workflow:\n'
    printf '  1. Use a worktree by default: git worktree add /workspaces/homelab-worktrees/<implementation> -b codex/<implementation> origin/main\n'
    printf '  2. Make tracked edits only on branch codex/<implementation>.\n'
    printf '  3. Keep durable Spec Kit artifacts in specs/<implementation>/.\n'
    printf '  4. After bootstrap, spec.md, plan.md, and tasks.md must be non-empty.\n'
    printf '  5. Before push or PR automation, evidence.md must be non-empty.\n'
  } >&2
  exit 1
}

implementation_from_branch() {
  [[ "$branch" =~ ^codex/.+ ]] || return 1
  printf '%s\n' "${branch#codex/}"
}

validate_branch() {
  if [[ "$branch" == "main" ]]; then
    fail "Current branch is main."
  fi
  if [[ ! "$branch" =~ ^codex/.+ ]]; then
    fail "Current branch '$branch' does not match codex/<implementation>."
  fi
}

require_sdd_artifact() {
  local path="$1"
  if [[ ! -s "$path" ]]; then
    fail "Missing required SDD artifact: $path"
  fi
}

validate_sdd_context() {
  validate_branch
  local implementation
  implementation="$(implementation_from_branch)"
  require_sdd_artifact "specs/$implementation/spec.md"
  require_sdd_artifact "specs/$implementation/plan.md"
  require_sdd_artifact "specs/$implementation/tasks.md"
}

validate_sdd_evidence() {
  validate_sdd_context
  local implementation
  implementation="$(implementation_from_branch)"
  require_sdd_artifact "specs/$implementation/evidence.md"
}

payload_mentions_evidence_path() {
  PAYLOAD="$payload" python3 - <<'PY'
import json
import os
import re
import sys

payload = os.environ.get("PAYLOAD", "")
haystacks = [payload]
try:
    data = json.loads(payload) if payload.strip() else {}
except json.JSONDecodeError:
    data = {}

def walk(value):
    if isinstance(value, str):
        haystacks.append(value)
    elif isinstance(value, dict):
        for nested in value.values():
            walk(nested)
    elif isinstance(value, list):
        for nested in value:
            walk(nested)

walk(data)
text = "\n".join(haystacks)
sys.exit(0 if re.search(r"specs/[^/\s]+/evidence\.md", text) else 1)
PY
}

is_allowed_tmp_payload() {
  PAYLOAD="$payload" python3 - <<'PY'
import json
import os
import re
import sys

payload = os.environ.get("PAYLOAD", "")
haystacks = [payload]
try:
    data = json.loads(payload) if payload.strip() else {}
except json.JSONDecodeError:
    data = {}

def walk(value):
    if isinstance(value, str):
        haystacks.append(value)
    elif isinstance(value, dict):
        for nested in value.values():
            walk(nested)
    elif isinstance(value, list):
        for nested in value:
            walk(nested)

walk(data)
text = "\n".join(haystacks)
paths = set(re.findall(r"(?:^|[\s\"'])((?:/[^/\s]+)*/?\.codex/tmp/repo-change-intent)(?:$|[\s\"'])", text))
sys.exit(0 if paths else 1)
PY
}

is_sdd_payload() {
  PAYLOAD="$payload" python3 - <<'PY'
import json
import os
import re
import sys

payload = os.environ.get("PAYLOAD", "")
haystacks = [payload]
try:
    data = json.loads(payload) if payload.strip() else {}
except json.JSONDecodeError:
    data = {}

def walk(value):
    if isinstance(value, str):
        haystacks.append(value)
    elif isinstance(value, dict):
        for nested in value.values():
            walk(nested)
    elif isinstance(value, list):
        for nested in value:
            walk(nested)

walk(data)
text = "\n".join(haystacks)
paths = set(re.findall(r"(?:/workspaces/[^/\s]+/[^/\s]+/)?specs/([^/\s]+)/((?:spec|plan|tasks|evidence)\.md)", text))
if not paths:
    sys.exit(1)
implementations = {implementation for implementation, _ in paths}
sys.exit(0 if len(implementations) == 1 else 1)
PY
}

sdd_artifacts_absent_from_head() {
  validate_branch
  local implementation
  implementation="$(implementation_from_branch)"
  local tracked_at_head
  tracked_at_head="$(
    git ls-tree -r --name-only HEAD "specs/$implementation" 2>/dev/null || true
  )"
  [[ -z "$tracked_at_head" ]]
}

tracked_changes_are_sdd_bootstrap() {
  validate_branch
  local implementation
  implementation="$(implementation_from_branch)"
  TRACKED_CHANGES="$(git status --porcelain --untracked-files=no)" IMPLEMENTATION="$implementation" python3 - <<'PY'
import os
import sys

implementation = os.environ["IMPLEMENTATION"]
allowed = {
    f"specs/{implementation}/spec.md",
    f"specs/{implementation}/plan.md",
    f"specs/{implementation}/tasks.md",
    f"specs/{implementation}/evidence.md",
}
paths = []
for line in os.environ.get("TRACKED_CHANGES", "").splitlines():
    path = line[3:]
    if " -> " in path:
        path = path.split(" -> ", 1)[1]
    paths.append(path)
sys.exit(0 if paths and set(paths) <= allowed else 1)
PY
}

command_is_allowed_worktree_setup() {
  PAYLOAD="$payload" ROOT="$root" python3 - <<'PY'
import json
import os
import shlex
import sys

payload = os.environ.get("PAYLOAD", "")
try:
    data = json.loads(payload) if payload.strip() else {}
except json.JSONDecodeError:
    data = {}

values = []
for key in ("command", "input", "tool_input"):
    value = data.get(key)
    if isinstance(value, str):
        values.append(value)
    elif isinstance(value, dict):
        for nested in ("command", "cmd"):
            if isinstance(value.get(nested), str):
                values.append(value[nested])

for value in values:
    try:
        lexer = shlex.shlex(value, posix=True, punctuation_chars=True)
        lexer.whitespace_split = True
        tokens = list(lexer)
    except ValueError:
        continue

    if tokens[:2] == ["mkdir", "-p"] and len(tokens) == 3:
        if tokens[2] in {"/workspaces/homelab-worktrees", "/workspaces/homelab-ideas"}:
            sys.exit(0)

    if len(tokens) >= 7 and tokens[:3] == ["git", "worktree", "add"]:
        destination = tokens[3]
        if destination.startswith(("/workspaces/homelab-worktrees/", "/workspaces/homelab-ideas/")):
            if "-b" in tokens:
                branch_index = tokens.index("-b") + 1
                if branch_index < len(tokens) and tokens[branch_index].startswith("codex/") and "origin/main" in tokens:
                    sys.exit(0)

sys.exit(1)
PY
}

payload_has_mutating_command() {
  PAYLOAD="$payload" python3 - <<'PY'
import json
import os
import shlex
import sys

payload = os.environ.get("PAYLOAD", "")
try:
    data = json.loads(payload) if payload.strip() else {}
except json.JSONDecodeError:
    data = {}

values = []
for key in ("command", "input", "tool_input"):
    value = data.get(key)
    if isinstance(value, str):
        values.append(value)
    elif isinstance(value, dict):
        for nested in ("command", "cmd"):
            if isinstance(value.get(nested), str):
                values.append(value[nested])

mutating_commands = {
    "apply_patch",
    "chmod",
    "chown",
    "cp",
    "git",
    "install",
    "ln",
    "mkdir",
    "mv",
    "pre-commit",
    "rm",
    "rsync",
    "sed",
    "sops",
    "terraform",
    "touch",
}
safe_git = {"branch", "diff", "log", "rev-parse", "show", "status"}
mutating_git = {
    "add",
    "am",
    "apply",
    "checkout",
    "cherry-pick",
    "clean",
    "commit",
    "merge",
    "mv",
    "pull",
    "push",
    "rebase",
    "reset",
    "restore",
    "revert",
    "switch",
    "tag",
    "worktree",
}
mutating_terraform = {"apply", "destroy", "fmt", "import", "init", "taint", "untaint", "workspace"}
separators = {";", "&&", "||", "|"}

for value in values:
    try:
        lexer = shlex.shlex(value, posix=True, punctuation_chars=True)
        lexer.whitespace_split = True
        tokens = list(lexer)
    except ValueError:
        continue

    index = 0
    while index < len(tokens):
        token = tokens[index]
        if token in separators:
            index += 1
            continue
        command = token.rsplit("/", 1)[-1]
        args = []
        index += 1
        while index < len(tokens) and tokens[index] not in separators:
            args.append(tokens[index])
            index += 1

        if command == "git":
            subcommand = next((arg for arg in args if not arg.startswith("-")), "")
            if subcommand in safe_git:
                continue
            if subcommand in mutating_git or subcommand:
                sys.exit(0)
        elif command == "terraform":
            subcommand = next((arg for arg in args if not arg.startswith("-chdir")), "")
            if subcommand in mutating_terraform:
                sys.exit(0)
        elif command == "sed" and any(arg.startswith("-i") for arg in args):
            sys.exit(0)
        elif command in mutating_commands:
            sys.exit(0)

sys.exit(1)
PY
}

if [[ "${1:-}" == "--preflight-mutation" ]]; then
  if is_allowed_tmp_payload; then
    exit 0
  fi
  if is_sdd_payload && sdd_artifacts_absent_from_head; then
    exit 0
  fi
  if payload_mentions_evidence_path; then
    validate_sdd_context
  else
    validate_sdd_context
  fi
  exit 0
fi

if [[ "${1:-}" == "--preflight-bash" ]]; then
  if command_is_allowed_worktree_setup; then
    exit 0
  fi
  if payload_has_mutating_command; then
    validate_sdd_context
  fi
  exit 0
fi

tracked_changes="$(git status --porcelain --untracked-files=no)"
head_now="$(git rev-parse HEAD)"
head_before="$head_now"
if [[ -f "$state_file" ]]; then
  head_before="$(awk -F= '$1 == "head" { print $2; exit }' "$state_file")"
fi

if [[ -z "$tracked_changes" && "$head_before" == "$head_now" ]]; then
  exit 0
fi

if tracked_changes_are_sdd_bootstrap && sdd_artifacts_absent_from_head; then
  exit 0
fi

validate_sdd_context
