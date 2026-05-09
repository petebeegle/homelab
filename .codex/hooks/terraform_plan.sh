#!/usr/bin/env bash
set -euo pipefail

payload="$(cat || true)"
root="$(git rev-parse --show-toplevel)"
cd "$root"

command_text="$(
  PAYLOAD="$payload" python3 - <<'PY'
import json
import os

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
print("\n".join(values))
PY
)"

if ! grep -Eq '(^|[;&|[:space:]])terraform[[:space:]]+apply($|[[:space:]])' <<<"$command_text"; then
  exit 0
fi

if ! command -v terraform >/dev/null 2>&1; then
  printf 'Codex Terraform guard: terraform apply was requested but terraform is not installed.\n' >&2
  exit 1
fi

mapfile -t dirs < <(
  git diff --name-only --diff-filter=ACMRTUXB HEAD -- 'terraform/**/*.tf' 'terraform/**/*.tfvars' 2>/dev/null |
    xargs -r -n1 dirname |
    sort -u
)

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
    printf 'Codex Terraform guard: skipping %s because it has not been initialized.\n' "$dir" >&2
    continue
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
