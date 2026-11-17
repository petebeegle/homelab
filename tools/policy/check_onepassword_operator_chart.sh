#!/usr/bin/env bash
set -euo pipefail

# Renders the committed 1Password HelmRelease and checks the properties that matter
# (direct service-account auth, no Connect, no token Secret, pinned operator image,
# polling interval, resources). Versions are read from the committed manifests, not
# hardcoded, so Renovate chart bumps are checked rather than rejected.

repo_root="${ONEPASSWORD_CHART_CHECK_ROOT:-$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." && pwd)}"
app_file="$repo_root/kubernetes/infra/controllers/onepassword-operator/app.yaml"
values_file="$repo_root/kubernetes/infra/controllers/onepassword-operator/values.yaml"

# First "chart:" in the HelmRelease spec, the "version:" that follows it, and the
# HelmRepository url.
chart_name="$(sed -nE 's/^ +chart: *"?([^" ]+)"?$/\1/p' "$app_file" | head -n1)"
chart_version="$(sed -nE '/^ +chart: *"?connect"?$/,/^ +version:/s/^ +version: *"?([^" ]+)"?$/\1/p' "$app_file" | head -n1)"
chart_repository="$(sed -nE 's/^ +url: *"?([^" ]+)"?$/\1/p' "$app_file" | head -n1)"
operator_version="$(sed -nE '/^operator:/,/^[^ ]/s/^  version: *"?([^" ]+)"?$/\1/p' "$values_file" | head -n1)"

if [ "$chart_name" != "connect" ]; then
	echo "1Password chart check: committed HelmRelease chart is '$chart_name', not connect" >&2
	exit 1
fi
for pin in chart_version chart_repository operator_version; do
	if [ -z "${!pin}" ]; then
		echo "1Password chart check: could not read $pin from the committed manifests" >&2
		exit 1
	fi
done

rendered="$(mktemp)"
rendered_values="$(mktemp)"

cleanup() {
	rm -f -- "$rendered" "$rendered_values"
}
trap cleanup EXIT

ONEPASSWORD_POLLING_INTERVAL=3600 flux envsubst --strict \
	< "$values_file" > "$rendered_values"

helm template onepassword-operator connect \
	--repo "$chart_repository" \
	--version "$chart_version" \
	--namespace onepassword-system \
	--values "$rendered_values" \
	> "$rendered"

if grep -Eq 'image: .*1password/connect-(api|sync)' "$rendered"; then
	echo "1Password chart check: Connect workload rendered unexpectedly" >&2
	exit 1
fi

if grep -Eq 'name: OP_CONNECT_(HOST|TOKEN)' "$rendered"; then
	echo "1Password chart check: Connect authentication environment rendered unexpectedly" >&2
	exit 1
fi

if ! grep -q 'name: OP_SERVICE_ACCOUNT_TOKEN' "$rendered"; then
	echo "1Password chart check: direct service-account authentication is missing" >&2
	exit 1
fi

if grep -q '^kind: Secret$' "$rendered"; then
	echo "1Password chart check: chart rendered a token-valued Secret" >&2
	exit 1
fi

if ! grep -Eq "image: .*1password/onepassword-operator:${operator_version//./\\.}([\"' ]|\$)" "$rendered"; then
	echo "1Password chart check: pinned operator image ${operator_version} is missing" >&2
	exit 1
fi

if ! grep -A1 'name: POLLING_INTERVAL' "$rendered" | grep -q 'value: "3600"'; then
	echo "1Password chart check: quota-safe production polling interval is missing" >&2
	exit 1
fi

if ! grep -A12 '^          resources:$' "$rendered" | grep -q 'cpu: 50m'; then
	echo "1Password chart check: operator resource requests are missing" >&2
	exit 1
fi

if ! grep -A12 '^          resources:$' "$rendered" | grep -q 'memory: 256Mi'; then
	echo "1Password chart check: operator resource limits are missing" >&2
	exit 1
fi

echo "1Password chart check: connect ${chart_version} renders the direct operator without Connect or token Secret."
