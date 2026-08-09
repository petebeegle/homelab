#!/usr/bin/env bash
set -euo pipefail

provider="${FLUX_BOOTSTRAP_SECRET_PROVIDER:-sops}"
age_key_file="${SOPS_AGE_KEY_FILE:-$HOME/.config/sops/age/keys.agekey}"
token_file=""

cleanup() {
	if [[ -n "$token_file" && -f "$token_file" ]]; then
		rm -f -- "$token_file"
	fi
}
trap cleanup EXIT

case "$provider" in
	sops | dual | onepassword) ;;
	*)
		echo "unsupported bootstrap secret provider: $provider" >&2
		exit 1
		;;
esac

command -v kubectl >/dev/null 2>&1 || {
	echo "kubectl is required to install Flux bootstrap secrets" >&2
	exit 1
}

if [[ "$provider" == "sops" || "$provider" == "dual" ]]; then
	if [[ ! -s "$age_key_file" ]]; then
		echo "SOPS Age key is missing or empty: $age_key_file" >&2
		exit 1
	fi

	kubectl create secret generic sops-age \
		--namespace=flux-system \
		--from-file=keys.agekey="$age_key_file" \
		--dry-run=client -o yaml | kubectl apply -f -
fi

if [[ "$provider" == "dual" || "$provider" == "onepassword" ]]; then
	command -v op >/dev/null 2>&1 || {
		echo "1Password CLI is required for bootstrap provider $provider" >&2
		exit 1
	}

	: "${OP_SERVICE_ACCOUNT_TOKEN_REF:?OP_SERVICE_ACCOUNT_TOKEN_REF is required for bootstrap provider $provider}"
	if [[ "$OP_SERVICE_ACCOUNT_TOKEN_REF" != op://* ]]; then
		echo "OP_SERVICE_ACCOUNT_TOKEN_REF must be an op:// secret reference" >&2
		exit 1
	fi

	token_file="$(mktemp)"
	chmod 600 "$token_file"
	if ! op read --no-newline "$OP_SERVICE_ACCOUNT_TOKEN_REF" >"$token_file"; then
		echo "failed to read the 1Password service-account token" >&2
		exit 1
	fi
	if [[ ! -s "$token_file" ]]; then
		echo "1Password service-account token reference returned an empty value" >&2
		exit 1
	fi

	kubectl create namespace onepassword-system \
		--dry-run=client -o yaml | kubectl apply -f -
	kubectl create secret generic onepassword-service-account-token \
		--namespace=onepassword-system \
		--from-file=token="$token_file" \
		--dry-run=client -o yaml | kubectl apply -f -
fi

echo "Flux bootstrap secrets installed for provider: $provider"
