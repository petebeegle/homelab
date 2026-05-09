#!/usr/bin/env bash
set -euo pipefail

root="$(git rev-parse --show-toplevel)"
cd "$root"

failed=0

if [[ -e .codex/hooks.json ]]; then
  printf 'Codex self-verify: .codex/hooks.json exists, but hooks must be inline in .codex/config.toml.\n' >&2
  failed=1
fi

for script in .codex/hooks/*.sh; do
  [[ -f "$script" ]] || continue
  if [[ ! -x "$script" ]]; then
    printf 'Codex self-verify: %s is not executable.\n' "$script" >&2
    failed=1
  fi
  bash -n "$script" || failed=1
done

python3 - <<'PY' || failed=1
import re
import sys

try:
    import tomllib
except ModuleNotFoundError:
    tomllib = None

for path in [
    ".codex/config.toml",
    ".codex/agents/verifier.toml",
    ".codex/agents/repo_migration_worker.toml",
    ".codex/agents/memory_agent_builder.toml",
    ".codex/agents/memory_consolidator.toml",
]:
    raw = open(path, "rb").read()
    if tomllib is not None:
        tomllib.loads(raw.decode("utf-8"))
        continue

    text = raw.decode("utf-8")
    if text.count('"""') % 2:
        raise SystemExit(f"{path}: unbalanced triple-quoted string")
    in_multiline = False
    for lineno, line in enumerate(text.splitlines(), 1):
        stripped = line.strip()
        if stripped.count('"""') % 2:
            in_multiline = not in_multiline
            continue
        if in_multiline:
            continue
        if not stripped or stripped.startswith("#"):
            continue
        if stripped.startswith("[") and stripped.endswith("]"):
            continue
        if "=" in stripped:
            continue
        if re.match(r"^[A-Za-z0-9_-]+$", stripped):
            continue
        raise SystemExit(f"{path}:{lineno}: unsupported TOML-like syntax: {line}")
PY

if ((failed)); then
  exit 1
fi
