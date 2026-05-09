#!/usr/bin/env bash
set -euo pipefail

root="$(git rev-parse --show-toplevel)"
cd "$root"

mapfile -t secret_files < <(
  git status --porcelain --untracked-files=all -- \
    'kubernetes/**/secret.yaml' \
    'kubernetes/**/grafana-env.yaml' \
    '**/secret.yaml' \
    '**/grafana-env.yaml' |
    awk '{print $2}' |
    sort -u
)

if ((${#secret_files[@]} == 0)); then
  exit 0
fi

failed=0
for file in "${secret_files[@]}"; do
  [[ -f "$file" ]] || continue

  if ! grep -Eq '^[[:space:]]*sops:' "$file"; then
    printf 'Codex SOPS guard: %s is a secret-like file without a top-level sops: block.\n' "$file" >&2
    failed=1
    continue
  fi

  if grep -Eq '^[[:space:]]*(stringData|data):[[:space:]]*$' "$file" &&
    ! grep -Eq 'ENC\[(AES256_GCM|age),' "$file"; then
    printf 'Codex SOPS guard: %s has Kubernetes secret data but no encrypted ENC[...] values.\n' "$file" >&2
    failed=1
  fi
done

if ((failed)); then
  cat >&2 <<'EOF'
Codex SOPS guard blocked this turn.
Encrypt secret manifests before continuing, for example:
  sops -i -e kubernetes/path/to/secret.yaml
EOF
  exit 1
fi
