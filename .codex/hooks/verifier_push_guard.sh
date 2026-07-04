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

branch="$(git branch --show-current)"
head_sha="$(git rev-parse HEAD)"

fail() {
  {
    printf 'Spec Kit push guard: refusing to push to origin.\n'
    printf '%s\n' "$1"
  } >&2
  exit 1
}

if [[ "$branch" == "main" ]]; then
  fail "Current branch is main."
fi

if [[ ! "$branch" =~ ^codex/.+ ]]; then
  fail "Current branch '$branch' does not match codex/<implementation>."
fi

implementation="${branch#codex/}"
for artifact in spec.md plan.md tasks.md evidence.md; do
  if [[ ! -s "specs/$implementation/$artifact" ]]; then
    fail "Missing required SDD artifact: specs/$implementation/$artifact"
  fi
done

if ! python3 tools/codex-harness/validate_sdd_context.py \
  --root "$root" \
  --branch "$branch" \
  --require-plan-artifacts \
  --require-evidence \
  --head "$head_sha" \
  2>/tmp/spec-kit-push-guard.err; then
  cat /tmp/spec-kit-push-guard.err >&2
  fail "SDD evidence validation failed."
fi
