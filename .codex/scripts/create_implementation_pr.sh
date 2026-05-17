#!/usr/bin/env bash
set -euo pipefail

root="$(git rev-parse --show-toplevel)"
cd "$root"

auto=0
if [[ "${1:-}" == "--auto" ]]; then
  auto=1
fi

branch="$(git branch --show-current)"
if [[ ! "$branch" =~ ^codex/.+ ]]; then
  if ((auto)); then
    exit 0
  fi
  printf 'Implementation PR: current branch must match codex/<implementation>, got %s.\n' "$branch" >&2
  exit 1
fi

head_sha="$(git rev-parse HEAD)"
approval_file=".codex/tmp/verifier-approved"
attestation_file=".codex/tmp/verifier-attestation.yaml"
if [[ ! -f "$approval_file" ]] || ! grep -Fxq "$head_sha" "$approval_file"; then
  if ((auto)); then
    exit 0
  fi
  {
    printf 'Implementation PR: verifier approval is missing for exact HEAD.\n'
    printf 'Expected %s to contain:\n' "$approval_file"
    printf '  %s\n' "$head_sha"
  } >&2
  exit 1
fi

if [[ ! -f "$attestation_file" ]]; then
  if ((auto)); then
    exit 0
  fi
  {
    printf 'Implementation PR: verifier attestation is missing for exact HEAD.\n'
    printf 'Expected %s with approved_head:\n' "$attestation_file"
    printf '  %s\n' "$head_sha"
  } >&2
  exit 1
fi

marker=".codex/tmp/active-implementation"
if [[ ! -f "$marker" ]]; then
  printf 'Implementation PR: missing %s.\n' "$marker" >&2
  exit 1
fi

run_root_python() {
  if [[ -f pyproject.toml && -f uv.lock ]] && command -v uv >/dev/null 2>&1; then
    uv run --frozen python3 "$@"
  else
    python3 "$@"
  fi
}

validator="tools/codex-harness/validate_active_implementation.py"
if ! run_root_python "$validator" --marker "$marker" --root "$root" --branch "$branch"; then
  printf 'Implementation PR: active implementation marker does not match this checkout.\n' >&2
  exit 1
fi

attestation_validator="tools/codex-harness/validate_workflow_attestations.py"
if ! run_root_python "$attestation_validator" --kind verifier --attestation "$attestation_file" --head "$head_sha" --root "$root" --branch "$branch"; then
  printf 'Implementation PR: verifier attestation validation failed.\n' >&2
  exit 1
fi

implementation="${branch#codex/}"

if [[ -n "$(git status --porcelain)" ]]; then
  printf 'Implementation PR: working tree must be clean before creating a PR.\n' >&2
  exit 1
fi

if ! command -v gh >/dev/null 2>&1; then
  printf 'Implementation PR: gh is required to create the pull request.\n' >&2
  exit 1
fi

title="Implementation: ${implementation}"
commit_summary="$(git log --oneline origin/main..HEAD)"
changed_files="$(git diff --name-only origin/main..HEAD)"
plan_summary_file=".codex/tmp/pr-summary.md"
body="$(mktemp)"
trap 'rm -f "$body"' EXIT

{
  printf '## Summary\n'
  if [[ -s "$plan_summary_file" ]]; then
    cat "$plan_summary_file"
    printf '\n'
  else
    printf 'Implements the `%s` implementation plan. Changes are isolated on `%s`, verified at `%s`, and ready for review.\n' "$implementation" "$branch" "$head_sha"
  fi
  printf '\n## Changes\n'
  if [[ -n "$changed_files" ]]; then
    printf '%s\n' "$changed_files" | sed 's/^/- /'
  else
    printf '%s\n' '- No files changed relative to origin/main.'
  fi
  printf '\n## Commits\n'
  if [[ -n "$commit_summary" ]]; then
    printf '%s\n' "$commit_summary" | sed 's/^/- /'
  else
    printf '%s\n' '- No commits found relative to origin/main.'
  fi
  printf '\n## Verification\n'
  printf '%s\n' "- Verified HEAD: \`$head_sha\`."
  printf '%s\n' "- Verifier approval recorded in \`$approval_file\`."
} >"$body"

git push -u origin "$branch"
gh pr create --base main --head "$branch" --title "$title" --body-file "$body"

parent="$(dirname "$root")"
expected_parent="/workspaces/homelab-ideas"
if [[ "$parent" != "$expected_parent" ]]; then
  printf 'Implementation PR: refusing to delete clone outside %s: %s\n' "$expected_parent" "$root" >&2
  exit 1
fi

cd "$parent"
rm -rf -- "$root"
