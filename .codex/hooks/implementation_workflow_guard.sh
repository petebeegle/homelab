#!/usr/bin/env bash
set -euo pipefail

root="$(git rev-parse --show-toplevel)"
cd "$root"

state_file=".codex/tmp/implementation-workflow-guard-state"
if [[ "${1:-}" == "--record" ]]; then
  mkdir -p .codex/tmp
  {
    printf 'branch=%s\n' "$(git branch --show-current)"
    printf 'head=%s\n' "$(git rev-parse HEAD)"
  } >"$state_file"
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

branch="$(git branch --show-current)"
marker=".codex/tmp/active-implementation"
validator="tools/codex-harness/validate_active_implementation.py"

fail() {
  {
    printf 'Implementation workflow guard: refusing tracked-file changes outside an active implementation.\n'
    printf '%s\n' "$1"
    printf '\nRequired workflow:\n'
    printf '  1. Clone https://github.com/petebeegle/homelab.git into /workspaces/homelab-ideas/<implementation>.\n'
    printf '  2. Create codex/<implementation> from origin/main.\n'
    printf '  3. Record %s with implementation, branch, base, role=implementation, clone_path, owner_role=implementation-agent, and owner_agent.\n' "$marker"
    printf '  4. Make tracked-file changes only inside that sibling clone.\n'
  } >&2
  exit 1
}

if [[ "$branch" == "main" ]]; then
  fail "Current branch is main and tracked files or HEAD changed."
fi

if [[ ! "$branch" =~ ^codex/.+ ]]; then
  fail "Current branch '$branch' does not match codex/<implementation>."
fi

if [[ ! -f "$marker" ]]; then
  fail "Missing $marker."
fi

if ! python3 "$validator" --marker "$marker" --root "$root" --branch "$branch"; then
  fail "Active implementation marker validation failed."
fi
