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
  printf 'Spec Kit PR: current branch must match codex/<implementation>, got %s.\n' "$branch" >&2
  exit 1
fi

implementation="${branch#codex/}"
head_sha="$(git rev-parse HEAD)"

for artifact in spec.md plan.md tasks.md evidence.md; do
  if [[ ! -s "specs/$implementation/$artifact" ]]; then
    printf 'Spec Kit PR: missing required SDD artifact: specs/%s/%s.\n' "$implementation" "$artifact" >&2
    exit 1
  fi
done

if ! python3 tools/codex-harness/validate_sdd_context.py \
  --root "$root" \
  --branch "$branch" \
  --require-plan-artifacts \
  --require-evidence \
  --head "$head_sha"; then
  printf 'Spec Kit PR: SDD evidence validation failed.\n' >&2
  exit 1
fi

if [[ -n "$(git status --porcelain)" ]]; then
  printf 'Spec Kit PR: working tree must be clean before creating a PR.\n' >&2
  exit 1
fi

if ! command -v gh >/dev/null 2>&1; then
  printf 'Spec Kit PR: gh is required to create the pull request.\n' >&2
  exit 1
fi

title="Implementation: ${implementation}"
commit_summary="$(git log --oneline origin/main..HEAD)"
changed_files="$(git diff --name-only origin/main..HEAD)"
body="$(mktemp)"
trap 'rm -f "$body"' EXIT

{
  printf '## Summary\n'
  if [[ -s "specs/$implementation/evidence.md" ]]; then
    sed -n '1,120p' "specs/$implementation/evidence.md"
    printf '\n'
  else
    printf 'Implements the `%s` Spec Kit plan on `%s`.\n' "$implementation" "$branch"
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
  printf '%s\n' "- Spec Kit evidence: \`specs/$implementation/evidence.md\`."
  printf '%s\n' "- HEAD: \`$head_sha\`."
} >"$body"

git push -u origin "$branch"
gh pr create --base main --head "$branch" --title "$title" --body-file "$body"
