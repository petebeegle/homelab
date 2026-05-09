#!/usr/bin/env bash
set -euo pipefail

root="$(git rev-parse --show-toplevel)"
cd "$root"

mapfile -t changed_kubernetes < <(
  git diff --name-only --diff-filter=ACMRTUXB HEAD -- 'kubernetes/**/*.yaml' 'kubernetes/**/*.yml' 2>/dev/null |
    sort -u
)

if ((${#changed_kubernetes[@]} == 0)); then
  exit 0
fi

if printf '%s\n' "${changed_kubernetes[@]}" | grep -Eq '^kubernetes/(clusters|apps|infra)/'; then
  cat >&2 <<'EOF'
Codex Flux reminder: Kubernetes manifests changed.
Before pushing, verify Flux dependencies, SOPS encryption, Gateway references, PVC StorageClass usage, and post-push Ready status for Kustomizations and HelmReleases.
EOF
fi
