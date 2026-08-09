# Operate the 1Password Kubernetes Operator

The homelab uses the official Helm chart named `connect`, but 1Password Connect is disabled. Each cluster runs the first-party operator with direct service-account authentication and a cluster-isolated, read-only 1Password service account.

## Credential boundaries

| Cluster | Readable vault | Bootstrap item reference |
| --- | --- | --- |
| development | `cluster development` | `op://cluster bootstrap/onepassword-development-operator/credential` |
| production | `cluster production` | `op://cluster bootstrap/onepassword-production-operator/credential` |

The `cluster bootstrap` vault is administrative storage for the service-account tokens. Operator service accounts must not be able to read it or the other cluster's vault. Do not export a service-account token, put it in `*.tfvars`, pass it as an argument, or print it. Terraform contains only the non-secret `op://` reference.

## Prepare production

Create a production service account with read-only access only to `cluster production`. Save its token in the `credential` field of `onepassword-production-operator` in `cluster bootstrap`. Create a disposable Login item named `k8s--onepassword-system--canary` in `cluster production`, with a non-empty built-in password field.

Sign in interactively and verify access without displaying values:

```bash
op read --no-newline \
  'op://cluster bootstrap/onepassword-production-operator/credential' \
  >/dev/null
op item get k8s--onepassword-system--canary \
  --vault 'cluster production' \
  --format=json >/dev/null
```

## Install bootstrap trust roots

Existing clusters can install the bootstrap Secrets without running Terraform. This keeps `sops-age` active while adding the operator token:

```bash
KUBECONFIG=/home/vscode/.kube/homelab-production.config \
FLUX_BOOTSTRAP_SECRET_PROVIDER=dual \
OP_SERVICE_ACCOUNT_TOKEN_REF='op://cluster bootstrap/onepassword-production-operator/credential' \
terraform/scripts/install-flux-bootstrap-secrets.sh
```

Expected output names both Secret objects and reports provider `dual`; it never contains their values. Verify metadata only:

```bash
kubectl --kubeconfig /home/vscode/.kube/homelab-production.config \
  -n flux-system get secret sops-age -o name
kubectl --kubeconfig /home/vscode/.kube/homelab-production.config \
  -n onepassword-system get secret onepassword-service-account-token -o name
```

## Verify reconciliation and rotation

After Flux applies the desired revision, verify the durable resources:

```bash
flux --kubeconfig /home/vscode/.kube/homelab-production.config \
  get kustomization onepassword-operator
kubectl --kubeconfig /home/vscode/.kube/homelab-production.config \
  -n onepassword-system get helmrelease onepassword-operator
kubectl --kubeconfig /home/vscode/.kube/homelab-production.config \
  -n onepassword-system rollout status deployment/onepassword-connect-operator \
  --timeout=10m
```

Run the disposable production canary:

```bash
python3 tools/development/verify_onepassword_operator.py \
  --vault 'cluster production' \
  --item k8s--onepassword-system--canary \
  --slug onepassword-prod-foundation \
  --kubeconfig /home/vscode/.kube/homelab-production.config \
  --timeout 10m
```

Success reports only the generated Secret resource-version transition, consuming pod UID transition, and namespace cleanup. Do not use `--keep` outside active debugging.

## Monitoring and diagnosis

Grafana alerts after ten minutes when the operator Deployment is absent/unavailable or a `OnePasswordItem` is not Ready. Start diagnosis with:

```bash
kubectl get onepassworditems.onepassword.com -A
kubectl -n onepassword-system get helmrelease,deployment,pods
kubectl -n onepassword-system logs deployment/onepassword-connect-operator --since=30m
```

A 1Password outage prevents refresh but does not remove an existing generated Secret. Confirm existing workloads remain running while investigating. Do not delete a durable `OnePasswordItem` as a diagnostic step: deletion also deletes its generated Kubernetes Secret.

## Rollback during foundation

All application consumers still use SOPS during the foundation phases. If the production operator cannot meet acceptance, leave `sops-age` and consumers untouched, suspend the `onepassword-operator` Flux Kustomization if needed for diagnosis, and revert the new foundation Git change. Remove only a disposable canary namespace whose ownership is certain.
