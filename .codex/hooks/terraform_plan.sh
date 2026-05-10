#!/usr/bin/env bash
set -euo pipefail

payload="$(cat || true)"
root="$(git rev-parse --show-toplevel)"
cd "$root"

command_analysis="$(
  PAYLOAD="$payload" python3 - <<'PY'
import json
import os
import shlex

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

separators = {";", "&&", "||", "|"}
apply_requested = False
target_dirs = []

for value in values:
    try:
        lexer = shlex.shlex(value, posix=True, punctuation_chars=True)
        lexer.whitespace_split = True
        tokens = list(lexer)
    except ValueError:
        continue

    index = 0
    while index < len(tokens):
        if tokens[index] != "terraform":
            index += 1
            continue

        args = []
        index += 1
        while index < len(tokens) and tokens[index] not in separators:
            args.append(tokens[index])
            index += 1

        chdir = None
        arg_index = 0
        while arg_index < len(args):
            arg = args[arg_index]
            if arg == "apply":
                apply_requested = True
                if chdir:
                    target_dirs.append(chdir)
                break
            if arg.startswith("-chdir="):
                chdir = arg.split("=", 1)[1]
            elif arg == "-chdir" and arg_index + 1 < len(args):
                chdir = args[arg_index + 1]
                arg_index += 1
            arg_index += 1

print(f"apply={1 if apply_requested else 0}")
for target_dir in target_dirs:
    print(f"dir={target_dir}")
PY
)"

if ! grep -qx 'apply=1' <<<"$command_analysis"; then
  exit 0
fi

if ! command -v terraform >/dev/null 2>&1; then
  printf 'Codex Terraform guard: terraform apply was requested but terraform is not installed.\n' >&2
  exit 1
fi

mapfile -t dirs < <(awk -F= '$1 == "dir" { print $2 }' <<<"$command_analysis" | sort -u)

if ((${#dirs[@]} == 0)); then
  mapfile -t dirs < <(
    git diff --name-only --diff-filter=ACMRTUXB HEAD -- 'terraform/**/*.tf' 'terraform/**/*.tfvars' 2>/dev/null |
      xargs -r -n1 dirname |
      sort -u
  )
fi

if ((${#dirs[@]} == 0)); then
  mapfile -t dirs < <(find terraform -mindepth 1 -maxdepth 3 -name '*.tf' -print | xargs -r -n1 dirname | sort -u)
fi

if ((${#dirs[@]} == 0)); then
  printf 'Codex Terraform guard: terraform apply requested, but no Terraform directories were found.\n' >&2
  exit 1
fi

for dir in "${dirs[@]}"; do
  [[ -d "$dir" ]] || continue
  if [[ ! -d "$dir/.terraform" ]]; then
    printf 'Codex Terraform guard: %s has not been initialized; run terraform init before apply.\n' "$dir" >&2
    exit 1
  fi

  printf 'Codex Terraform guard: running terraform plan in %s before apply.\n' "$dir" >&2
  set +e
  (cd "$dir" && terraform plan -detailed-exitcode -input=false -no-color)
  status=$?
  set -e

  case "$status" in
    0|2) ;;
    *)
      printf 'Codex Terraform guard: terraform plan failed in %s; apply is blocked.\n' "$dir" >&2
      exit "$status"
      ;;
  esac
done
