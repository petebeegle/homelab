#!/bin/bash

kubectl create namespace flux-system

cat ~/.config/sops/age/keys.agekey |
kubectl create secret generic sops-age \
	--namespace=flux-system \
	--from-file=keys.agekey=/dev/stdin

kubectl apply -f https://github.com/kubernetes-sigs/gateway-api/releases/download/v1.2.0/standard-install.yaml

flux bootstrap github \
	--owner=$GITHUB_USER \
	--repository=homelab \
	--branch=main \
	--path=./kubernetes/clusters/production \
	--personal
