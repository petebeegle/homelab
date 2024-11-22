#!/bin/bash

mkdir -p ~/.kube
echo "${kubeconfig}" > ~/.kube/config
chmod 600 ~/.kube/config
