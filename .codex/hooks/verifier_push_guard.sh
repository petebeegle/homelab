#!/usr/bin/env bash
set -euo pipefail

remote_name="${PRE_COMMIT_REMOTE_NAME:-}"
remote_url="${PRE_COMMIT_REMOTE_URL:-}"

if [[ -z "$remote_name" && -z "$remote_url" ]]; then
  remote_name="${1:-}"
  remote_url="${2:-}"
fi

explicit_pre_push_remote=0
if [[ -n "$remote_name" || -n "$remote_url" ]]; then
  explicit_pre_push_remote=1
fi

root="$(git rev-parse --show-toplevel)"
cd "$root"

origin_url="$(git remote get-url origin 2>/dev/null || true)"

if [[ -z "$remote_name" && -n "$remote_url" && -n "$origin_url" && "$remote_url" == "$origin_url" ]]; then
  remote_name="origin"
fi

if [[ -z "$remote_name" && "$explicit_pre_push_remote" -eq 0 ]]; then
  upstream="$(git rev-parse --abbrev-ref --symbolic-full-name '@{upstream}' 2>/dev/null || true)"
  if [[ "$upstream" == */* ]]; then
    remote_name="${upstream%%/*}"
  fi
fi

if [[ "$remote_name" != "origin" ]]; then
  exit 0
fi

head_sha="$(git rev-parse HEAD)"
approval_file=".codex/tmp/verifier-approved"
attestation_file=".codex/tmp/verifier-attestation.yaml"
attestation_validator="tools/codex-harness/validate_workflow_attestations.py"

if [[ ! -f "$approval_file" ]] || ! grep -Fxq "$head_sha" "$approval_file"; then
  {
    printf 'Verifier push guard: refusing to push to origin.\n'
    printf 'Expected %s to contain the exact HEAD SHA:\n' "$approval_file"
    printf '  %s\n' "$head_sha"
    printf 'Run verifier-agent review, resolve any blockers, then record approval for the exact HEAD before pushing.\n'
  } >&2
  exit 1
fi

if [[ ! -f "$attestation_file" ]]; then
  {
    printf 'Verifier push guard: refusing to push to origin.\n'
    printf 'Expected %s to contain verifier identity and exact approved_head:\n' "$attestation_file"
    printf '  %s\n' "$head_sha"
  } >&2
  exit 1
fi

if ! python3 "$attestation_validator" --kind verifier --attestation "$attestation_file" --head "$head_sha"; then
  printf 'Verifier push guard: verifier attestation validation failed.\n' >&2
  exit 1
fi
