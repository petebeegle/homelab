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

fail() {
  {
    printf 'Implementation workflow guard: refusing tracked-file changes outside an active implementation.\n'
    printf '%s\n' "$1"
    printf '\nRequired workflow:\n'
    printf '  1. Clone https://github.com/petebeegle/homelab.git into /workspaces/homelab-ideas/<implementation>.\n'
    printf '  2. Create codex/<implementation> from origin/main.\n'
    printf '  3. Record %s with implementation, branch, base, role=implementation, and clone_path.\n' "$marker"
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

expected_implementation="${branch#codex/}"
expected_clone="/workspaces/homelab-ideas/$expected_implementation"

get_marker_value() {
  local key="$1"
  awk -F= -v key="$key" '
    $1 == key {
      value = $0
      sub(/^[^=]*=/, "", value)
      gsub(/^"|"$/, "", value)
      print value
      exit
    }
  ' "$marker"
}

marker_implementation="$(get_marker_value implementation)"
marker_branch="$(get_marker_value branch)"
marker_role="$(get_marker_value role)"
marker_clone_path="$(get_marker_value clone_path)"

if [[ "$marker_implementation" != "$expected_implementation" ]]; then
  fail "$marker has implementation='$marker_implementation', expected '$expected_implementation'."
fi

if [[ "$marker_branch" != "$branch" ]]; then
  fail "$marker has branch='$marker_branch', expected '$branch'."
fi

if [[ "$marker_role" != "implementation" ]]; then
  fail "$marker has role='$marker_role', expected 'implementation'."
fi

if [[ "$marker_clone_path" != "$expected_clone" ]]; then
  fail "$marker has clone_path='$marker_clone_path', expected '$expected_clone'."
fi

if [[ "$root" != "$expected_clone" ]]; then
  fail "Current checkout is '$root', expected sibling clone '$expected_clone'."
fi
