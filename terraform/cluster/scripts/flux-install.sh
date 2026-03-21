#!/bin/bash
set -e

kubectl create secret generic sops-age \
	--namespace=flux-system \
	--from-file=keys.agekey="$HOME/.config/sops/age/keys.agekey" \
	--dry-run=client -o yaml | kubectl apply -f -

# Retry bootstrap up to 3 times to handle CRD registration race on fresh clusters
for i in 1 2 3; do
  flux bootstrap github \
    --owner=$GITHUB_USER \
    --repository=homelab \
    --branch=main \
    --path=./kubernetes/clusters/production \
    --personal && break
  echo "flux bootstrap attempt $i failed, retrying in 15s..."
  sleep 15
done
