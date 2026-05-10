#!/usr/bin/env bash
set -euo pipefail
umask 077

usage() {
  {
    printf 'Usage: %s <implementation> [repo-relative-secret-path ...]\n' "${0##*/}"
    printf '\n'
    printf 'Stages ignored local secret/config files for an implementation clone.\n'
    printf 'When no paths are provided, common ignored files are discovered: terraform.tfvars, *.tfvars, kubeconfig, talosconfig, .kube/config, and .talos/config.\n'
  } >&2
}

if [[ $# -lt 1 ]]; then
  usage
  exit 2
fi

implementation="$1"
shift

if [[ ! "$implementation" =~ ^[a-z0-9][a-z0-9._-]*$ ]]; then
  printf 'Secret staging: implementation must be a safe slug, got %s.\n' "$implementation" >&2
  exit 2
fi

root="$(git rev-parse --show-toplevel)"
cd "$root"

dest=".codex/tmp/implementation-secrets/$implementation"
tmp_dest=".codex/tmp/implementation-secrets/.staging-$implementation-$$"
rm -rf -- "$tmp_dest"
mkdir -p -- "$tmp_dest"
cleanup() {
  rm -rf -- "$tmp_dest"
}
trap cleanup EXIT

paths=("$@")
if [[ ${#paths[@]} -eq 0 ]]; then
  for candidate in terraform.tfvars kubeconfig talosconfig .kube/config .talos/config; do
    [[ -e "$candidate" ]] && paths+=("$candidate")
  done
  while IFS= read -r path; do
    paths+=("$path")
  done < <(git ls-files --others -i --exclude-standard -- '*.tfvars' 2>/dev/null || true)
fi

if [[ ${#paths[@]} -eq 0 ]]; then
  printf 'Secret staging: no local ignored secret/config files found for %s.\n' "$implementation" >&2
  exit 0
fi

manifest="$tmp_dest/MANIFEST.txt"
{
  printf 'implementation=%s\n' "$implementation"
  printf 'source_root=%s\n' "$root"
  printf 'paths:\n'
} >"$manifest"

staged=0
for rel in "${paths[@]}"; do
  if [[ "$rel" = /* || "$rel" == *..* ]]; then
    printf 'Secret staging: refusing unsafe path %s.\n' "$rel" >&2
    exit 1
  fi

  if [[ ! -e "$rel" ]]; then
    printf 'Secret staging: skipping missing path %s.\n' "$rel" >&2
    continue
  fi

  if git ls-files --error-unmatch -- "$rel" >/dev/null 2>&1; then
    printf 'Secret staging: refusing tracked path %s.\n' "$rel" >&2
    exit 1
  fi

  if ! git check-ignore -q -- "$rel"; then
    printf 'Secret staging: refusing non-ignored path %s.\n' "$rel" >&2
    exit 1
  fi

  mkdir -p -- "$tmp_dest/$(dirname "$rel")"
  if [[ -d "$rel" ]]; then
    cp -a -- "$rel" "$tmp_dest/$rel"
  else
    cp -p -- "$rel" "$tmp_dest/$rel"
  fi
  printf -- '- %s\n' "$rel" >>"$manifest"
  staged=$((staged + 1))
done

rm -rf -- "$dest"
mv -- "$tmp_dest" "$dest"
trap - EXIT
printf 'Secret staging: staged %s path(s) for %s under %s.\n' "$staged" "$implementation" "$dest"
