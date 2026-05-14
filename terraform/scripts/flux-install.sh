#!/bin/bash
set -euo pipefail

: "${FLUX_BOOTSTRAP_PATH:?FLUX_BOOTSTRAP_PATH is required}"
: "${GITHUB_USER:?GITHUB_USER is required}"

flux_branch="${FLUX_BOOTSTRAP_BRANCH:-main}"

kubectl create secret generic sops-age \
	--namespace=flux-system \
	--from-file=keys.agekey="$HOME/.config/sops/age/keys.agekey" \
	--dry-run=client -o yaml | kubectl apply -f -

# Retry bootstrap up to 3 times to handle CRD registration races on fresh clusters.
for i in 1 2 3; do
	flux bootstrap github \
		--owner="$GITHUB_USER" \
		--repository=homelab \
		--branch="$flux_branch" \
		--path="$FLUX_BOOTSTRAP_PATH" \
		--personal && break
	echo "flux bootstrap attempt $i failed, retrying in 15s..."
	sleep 15
done
