#!/usr/bin/env bash
set -euo pipefail
umask 077

usage() {
  {
    printf 'Usage: %s <implementation> [checkout-path ...]\n' "${0##*/}"
    printf '\n'
    printf 'Stages terraform/development/terraform.tfvars from this checkout and installs it into implementation worktrees or clones before development smoke.\n'
    printf 'When no path is provided, installs into /workspaces/homelab-worktrees/<implementation>.\n'
  } >&2
}

fail() {
  printf 'Development smoke secret prep: %s\n' "$*" >&2
  exit 1
}

if [[ $# -lt 1 ]]; then
  usage
  exit 2
fi

implementation="$1"
shift

if [[ ! "$implementation" =~ ^[a-z0-9][a-z0-9._-]*$ ]]; then
  fail "implementation must be a safe slug, got $implementation."
fi

root="$(git rev-parse --show-toplevel)"
cd "$root"

tfvars_path="terraform/development/terraform.tfvars"
if [[ ! -f "$tfvars_path" ]]; then
  fail "required ignored file is missing: $tfvars_path"
fi

if git ls-files --error-unmatch -- "$tfvars_path" >/dev/null 2>&1; then
  fail "refusing tracked file: $tfvars_path"
fi

if ! git check-ignore -q -- "$tfvars_path"; then
  fail "refusing non-ignored file: $tfvars_path"
fi

checkouts=("$@")
if [[ ${#checkouts[@]} -eq 0 ]]; then
  checkouts=("/workspaces/homelab-worktrees/$implementation")
fi

for checkout in "${checkouts[@]}"; do
  [[ -d "$checkout" ]] || fail "checkout path not found: $checkout"
  git -C "$checkout" rev-parse --show-toplevel >/dev/null 2>&1 ||
    fail "checkout path is not a Git checkout: $checkout"
done

stage_script="$root/.codex/scripts/stage_implementation_secrets.sh"
install_script="$root/.codex/scripts/install_implementation_secrets.sh"
[[ -x "$stage_script" ]] || fail "stage script is not executable: $stage_script"
[[ -x "$install_script" ]] || fail "install script is not executable: $install_script"

"$stage_script" "$implementation" "$tfvars_path"

stage_root="$root/.codex/tmp/implementation-secrets/$implementation"
[[ -d "$stage_root" ]] || fail "staged secret root was not created: $stage_root"

find "$stage_root" -type d -exec chmod 700 {} +
while IFS= read -r -d '' staged_file; do
  [[ "${staged_file#$stage_root/}" == "MANIFEST.txt" ]] && continue
  chmod 600 "$staged_file"
done < <(find "$stage_root" -type f -print0)

for checkout in "${checkouts[@]}"; do
  (cd "$checkout" && "$install_script" "$implementation" "$stage_root")
done

printf 'Development smoke secret prep: installed %s into %s checkout(s) for %s.\n' \
  "$tfvars_path" "${#checkouts[@]}" "$implementation"
