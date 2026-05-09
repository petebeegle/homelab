#!/usr/bin/env bash
set -euo pipefail

root="$(git rev-parse --show-toplevel)"
cd "$root"

if ! command -v pre-commit >/dev/null 2>&1; then
  printf 'Codex pre-commit check: pre-commit is not installed; skipping.\n' >&2
  exit 0
fi

mapfile -t changed_files < <(
  {
    git diff --name-only --diff-filter=ACMRTUXB HEAD -- 2>/dev/null
    git ls-files --others --exclude-standard
  } | sort -u
)

if ((${#changed_files[@]} == 0)); then
  exit 0
fi

printf 'Codex pre-commit check: running hooks for changed files.\n' >&2
pre-commit run --files "${changed_files[@]}"
