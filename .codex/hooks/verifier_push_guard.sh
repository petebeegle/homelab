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
marker=".codex/tmp/active-implementation"
plan=".codex/tmp/implementation-plan.yaml"
owner_attestation=".codex/tmp/implementation-owner-attestation.yaml"
marker_validator="tools/codex-harness/validate_active_implementation.py"
plan_validator="tools/codex-harness/validate_implementation_plan.py"
attestation_validator="tools/codex-harness/validate_workflow_attestations.py"
sdd_validator="tools/codex-harness/validate_sdd_context.py"
push_updates="$(cat || true)"

allow_smoke_push() {
  local branch
  branch="$(git branch --show-current)"
  [[ "$branch" =~ ^codex/.+ ]] || return 1
  [[ -n "$push_updates" ]] || return 1

  if ! PUSH_UPDATES="$push_updates" BRANCH="$branch" HEAD_SHA="$head_sha" python3 - <<'PY'
import os
import sys

branch = os.environ["BRANCH"]
head = os.environ["HEAD_SHA"]
updates = [line.split() for line in os.environ.get("PUSH_UPDATES", "").splitlines() if line.strip()]
if not updates:
    sys.exit(1)

remote_ref = f"refs/heads/{branch}"
for fields in updates:
    if len(fields) != 4:
        sys.exit(1)
    local_ref, local_oid, pushed_remote_ref, _remote_oid = fields
    if pushed_remote_ref != remote_ref:
        sys.exit(1)
    if local_oid != head:
        sys.exit(1)
    if local_ref not in {"HEAD", remote_ref}:
        sys.exit(1)
sys.exit(0)
PY
  then
    return 1
  fi

  python3 "$marker_validator" --marker "$marker" --root "$root" --branch "$branch" || return 1
  python3 "$plan_validator" --plan "$plan" --marker "$marker" --root "$root" --branch "$branch" || return 1
  python3 "$attestation_validator" --kind owner --attestation "$owner_attestation" --marker "$marker" --plan "$plan" --root "$root" --branch "$branch" || return 1
  python3 "$sdd_validator" --marker "$marker" --root "$root" --branch "$branch" --require-plan-artifacts || return 1
  return 0
}

if [[ ! -f "$approval_file" ]] || ! grep -Fxq "$head_sha" "$approval_file"; then
  if allow_smoke_push; then
    exit 0
  fi
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

if ! python3 "$attestation_validator" --kind verifier --attestation "$attestation_file" --marker "$marker" --owner-attestation "$owner_attestation" --head "$head_sha" --root "$root" --branch "$(git branch --show-current)"; then
  printf 'Verifier push guard: verifier attestation validation failed.\n' >&2
  exit 1
fi
