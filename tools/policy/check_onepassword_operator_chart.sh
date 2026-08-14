#!/usr/bin/env bash
set -euo pipefail

chart_version="2.4.1"
operator_version="1.12.0"
chart_repository="https://1password.github.io/connect-helm-charts"
repo_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." && pwd)"
values_file="$repo_root/kubernetes/infra/controllers/onepassword-operator/values.yaml"
rendered="$(mktemp)"
rendered_values="$(mktemp)"

if ! grep -q 'chart: connect' "$repo_root/kubernetes/infra/controllers/onepassword-operator/app.yaml" || \
	! grep -q 'version: "2.4.1"' "$repo_root/kubernetes/infra/controllers/onepassword-operator/app.yaml"; then
	echo "1Password chart check: committed HelmRelease chart pin is not connect 2.4.1" >&2
	exit 1
fi

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

if ! grep -q 'image: .*1password/onepassword-operator:1.12.0' "$rendered"; then
	echo "1Password chart check: pinned operator image is missing" >&2
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

echo "1Password chart check: direct operator rendered without Connect or token Secret."
