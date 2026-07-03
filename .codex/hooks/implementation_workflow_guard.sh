#!/usr/bin/env bash
set -euo pipefail

root="$(git rev-parse --show-toplevel)"
cd "$root"

payload="$(cat || true)"
state_file=".codex/tmp/implementation-workflow-guard-state"
if [[ "${1:-}" == "--record" ]]; then
  mkdir -p .codex/tmp
  {
    printf 'branch=%s\n' "$(git branch --show-current)"
    printf 'head=%s\n' "$(git rev-parse HEAD)"
  } >"$state_file"
  exit 0
fi

marker=".codex/tmp/active-implementation"
plan=".codex/tmp/implementation-plan.yaml"
owner_attestation=".codex/tmp/implementation-owner-attestation.yaml"
marker_validator="tools/codex-harness/validate_active_implementation.py"
plan_validator="tools/codex-harness/validate_implementation_plan.py"
attestation_validator="tools/codex-harness/validate_workflow_attestations.py"
sdd_validator="tools/codex-harness/validate_sdd_context.py"
branch="$(git branch --show-current)"

fail() {
  {
    printf 'Implementation workflow guard: refusing tracked-file changes outside an active implementation.\n'
    printf '%s\n' "$1"
    printf '\nRequired workflow:\n'
    printf '  1. Clone https://github.com/petebeegle/homelab.git into /workspaces/homelab-ideas/<implementation>.\n'
    printf '  2. Create codex/<implementation> from origin/main.\n'
    printf '  3. Record %s with implementation, branch, base, role=implementation, clone_path, owner_role=implementation-agent, and owner_agent.\n' "$marker"
    printf '  4. Record %s with implementation identity, scope, planned changes, docs impact, tests, verification, and risks.\n' "$plan"
    printf '  5. Record %s with role=implementation-agent, agent_id matching owner_agent, clone identity, and created_at.\n' "$owner_attestation"
    printf '  6. Create durable specs/<implementation>/spec.md, plan.md, tasks.md, and evidence.md from the Spec Kit templates.\n'
    printf '  7. Make tracked-file changes only inside that sibling clone.\n'
  } >&2
  exit 1
}

validate_workflow_base() {
  if [[ "$branch" == "main" ]]; then
    fail "Current branch is main."
  fi

  if [[ ! "$branch" =~ ^codex/.+ ]]; then
    fail "Current branch '$branch' does not match codex/<implementation>."
  fi

  if [[ ! -f "$marker" ]]; then
    fail "Missing $marker."
  fi

  if ! python3 "$marker_validator" --marker "$marker" --root "$root" --branch "$branch"; then
    fail "Active implementation marker validation failed."
  fi

  if [[ ! -f "$plan" ]]; then
    fail "Missing $plan."
  fi

  if ! python3 "$plan_validator" --plan "$plan" --marker "$marker" --root "$root" --branch "$branch"; then
    fail "Implementation plan validation failed."
  fi

  if [[ ! -f "$owner_attestation" ]]; then
    fail "Missing $owner_attestation."
  fi

  if ! python3 "$attestation_validator" --kind owner --attestation "$owner_attestation" --marker "$marker" --plan "$plan" --root "$root" --branch "$branch"; then
    fail "Implementation owner attestation validation failed."
  fi
}

validate_sdd_context() {
  if ! python3 "$sdd_validator" --marker "$marker" --root "$root" --branch "$branch" --require-plan-artifacts; then
    fail "SDD context validation failed."
  fi
}

validate_sdd_evidence() {
  if ! python3 "$sdd_validator" --marker "$marker" --root "$root" --branch "$branch" --require-plan-artifacts --require-evidence --head "$(git rev-parse HEAD)"; then
    fail "SDD evidence validation failed."
  fi
}

validate_workflow() {
  validate_workflow_base
  validate_sdd_context
}

payload_mentions_verifier_evidence() {
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
if re.search(r"(?:/workspaces/homelab-ideas/[^/\s]+/)?\.codex/tmp/(?:verifier-approved|verifier-attestation\.yaml)", text):
    sys.exit(0)
sys.exit(1)
PY
}

is_sdd_bootstrap_payload() {
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
paths = set(re.findall(r"(?:/workspaces/homelab-ideas/[^/\s]+/)?specs/([^/\s]+)/((?:spec|plan|tasks|evidence)\.md)", text))
if paths:
    implementations = {implementation for implementation, _ in paths}
    files = {name for _, name in paths}
    if len(implementations) == 1 and files <= {"spec.md", "plan.md", "tasks.md", "evidence.md"}:
        sys.exit(0)
sys.exit(1)
PY
}

tracked_changes_are_sdd_bootstrap() {
  python3 - "$branch" <<'PY'
import subprocess
import sys

branch = sys.argv[1]
if not branch.startswith("codex/"):
    sys.exit(1)
implementation = branch.split("/", 1)[1]
allowed = {
    f"specs/{implementation}/spec.md",
    f"specs/{implementation}/plan.md",
    f"specs/{implementation}/tasks.md",
    f"specs/{implementation}/evidence.md",
}
result = subprocess.run(
    ["git", "status", "--porcelain", "--untracked-files=no"],
    stdout=subprocess.PIPE,
    stderr=subprocess.DEVNULL,
    text=True,
    check=False,
)
paths = []
for line in result.stdout.splitlines():
    path = line[3:]
    if " -> " in path:
        path = path.split(" -> ", 1)[1]
    paths.append(path)

tracked_at_head = subprocess.run(
    ["git", "ls-tree", "-r", "--name-only", "HEAD", f"specs/{implementation}"],
    stdout=subprocess.PIPE,
    stderr=subprocess.DEVNULL,
    text=True,
    check=False,
)

if paths and set(paths) <= allowed and not tracked_at_head.stdout.strip():
    sys.exit(0)
sys.exit(1)
PY
}

sdd_artifacts_absent_from_head() {
  python3 - "$branch" <<'PY'
import subprocess
import sys

branch = sys.argv[1]
if not branch.startswith("codex/"):
    sys.exit(1)
implementation = branch.split("/", 1)[1]
result = subprocess.run(
    ["git", "ls-tree", "-r", "--name-only", "HEAD", f"specs/{implementation}"],
    stdout=subprocess.PIPE,
    stderr=subprocess.DEVNULL,
    text=True,
    check=False,
)
sys.exit(0 if not result.stdout.strip() else 1)
PY
}

if [[ "${1:-}" == "--preflight-mutation" ]]; then
  if PAYLOAD="$payload" python3 - <<'PY'
import json
import os
import re
import sys

payload = os.environ.get("PAYLOAD", "")
allowed = {
    ".codex/tmp/active-implementation",
    ".codex/tmp/implementation-plan.yaml",
    ".codex/tmp/implementation-owner-attestation.yaml",
    ".codex/tmp/repo-change-intent",
}

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

paths = set(re.findall(r"(?:/workspaces/homelab-ideas/[^/\s]+/)?\.codex/tmp/(?:active-implementation|implementation-plan\.yaml|implementation-owner-attestation\.yaml|repo-change-intent)", text))
normalized = {path[path.index(".codex/tmp/") :] for path in paths}

if normalized and normalized <= allowed:
    # Allow bootstrapping the local workflow artifacts that make validation possible.
    sys.exit(0)
sys.exit(1)
PY
  then
    exit 0
  fi
  if is_sdd_bootstrap_payload && sdd_artifacts_absent_from_head; then
    validate_workflow_base
    exit 0
  fi
  if payload_mentions_verifier_evidence; then
    validate_workflow_base
    validate_sdd_evidence
    exit 0
  fi
  validate_workflow
  exit 0
fi

if [[ "${1:-}" == "--preflight-bash" ]]; then
  if PAYLOAD="$payload" ROOT="$root" python3 - <<'PY'
import json
import os
import shlex
import sys

payload = os.environ.get("PAYLOAD", "")
root = os.environ.get("ROOT", "")
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
    "rm",
    "switch",
    "tag",
}
safe_git = {"branch", "diff", "log", "rev-parse", "show", "status"}
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
            if subcommand == "clone" and any(arg == "https://github.com/petebeegle/homelab.git" for arg in args) and any(
                arg.startswith("/workspaces/homelab-ideas/") for arg in args
            ):
                continue
            if (
                root.startswith("/workspaces/homelab-ideas/")
                and subcommand in {"switch", "checkout"}
                and any(arg == "-c" or arg == "-b" for arg in args)
                and any(arg.startswith("codex/") for arg in args)
                and any(arg == "origin/main" for arg in args)
            ):
                continue
            if subcommand in mutating_git or subcommand:
                sys.exit(0)
        elif command == "mkdir" and args == ["-p", ".codex/tmp"]:
            continue
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
  then
    if payload_mentions_verifier_evidence; then
      validate_workflow_base
      validate_sdd_evidence
    else
      validate_workflow
    fi
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

if tracked_changes_are_sdd_bootstrap; then
  validate_workflow_base
  exit 0
fi

validate_workflow
