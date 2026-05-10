#!/usr/bin/env bash
set -euo pipefail
umask 077

usage() {
  {
    printf 'Usage: %s <implementation> [staged-secret-root]\n' "${0##*/}"
    printf '\n'
    printf 'Installs staged local secret/config files into identical repo-relative paths in the current clone.\n'
  } >&2
}

if [[ $# -lt 1 || $# -gt 2 ]]; then
  usage
  exit 2
fi

implementation="$1"
source_root="${2:-/workspaces/homelab/.codex/tmp/implementation-secrets/$implementation}"

if [[ ! "$implementation" =~ ^[a-z0-9][a-z0-9._-]*$ ]]; then
  printf 'Secret install: implementation must be a safe slug, got %s.\n' "$implementation" >&2
  exit 2
fi

root="$(git rev-parse --show-toplevel)"
cd "$root"

if [[ ! -d "$source_root" ]]; then
  printf 'Secret install: staged secret root not found: %s\n' "$source_root" >&2
  exit 1
fi

installed=0
while IFS= read -r -d '' source_path; do
  rel="${source_path#"$source_root"/}"
  [[ "$rel" == "MANIFEST.txt" ]] && continue

  if [[ "$rel" = /* || "$rel" == *..* ]]; then
    printf 'Secret install: refusing unsafe staged path %s.\n' "$rel" >&2
    exit 1
  fi

  if git ls-files --error-unmatch -- "$rel" >/dev/null 2>&1; then
    printf 'Secret install: refusing to overwrite tracked path %s.\n' "$rel" >&2
    exit 1
  fi

  mkdir -p -- "$(dirname "$rel")"
  install -m 600 -- "$source_path" "$rel"
  installed=$((installed + 1))
done < <(find "$source_root" -type f -print0)

printf 'Secret install: installed %s path(s) for %s into %s.\n' "$installed" "$implementation" "$root"
