#!/usr/bin/env bash
# Put each Terraform root's terraform.tfvars in place from 1Password, without printing it.
#
#   tools/terraform/fetch_tfvars.sh [root ...]     (default: every root)
#
# Each file is the 1Password document "Terraform tfvars <root>" in the "cluster bootstrap"
# vault (docs/runbooks/terraform-state.md). A file already in place is kept, never
# overwritten. Needs a signed-in `op`.
set -euo pipefail

ROOTS=(development external/grafana external/nexus external/synology production)
VAULT="cluster bootstrap"
repo="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

wanted=("$@")
[ ${#wanted[@]} -gt 0 ] || wanted=("${ROOTS[@]}")
for root in "${wanted[@]}"; do
  case " ${ROOTS[*]} " in
    *" $root "*) ;;
    *) echo "unknown root: $root (known: ${ROOTS[*]})" >&2; exit 2 ;;
  esac
done

failed=0
for root in "${wanted[@]}"; do
  target="$repo/terraform/$root/terraform.tfvars"
  if [ -e "$target" ]; then
    echo "$root: kept the terraform.tfvars already there"
    continue
  fi
  partial="$repo/terraform/$root/terraform.fetching.tfvars"
  rm -f "$partial"
  if op document get "Terraform tfvars $root" --vault "$VAULT" --out-file "$partial" --file-mode 0600 >/dev/null; then
    chmod 600 "$partial"
    mv "$partial" "$target"
    echo "$root: fetched"
  else
    rm -f "$partial"
    echo "$root: could not fetch \"Terraform tfvars $root\" from the \"$VAULT\" vault" >&2
    failed=1
  fi
done
exit "$failed"
