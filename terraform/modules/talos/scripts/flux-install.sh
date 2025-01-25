#!/bin/bash
cat ~/.config/sops/age/keys.agekey |
kubectl create secret generic sops-age \
	--namespace=flux-system \
	--from-file=keys.agekey=/dev/stdin

flux bootstrap github \
	--owner=$GITHUB_USER \
	--repository=homelab \
	--branch=main \
	--path=./kubernetes/clusters/production \
	--personal
