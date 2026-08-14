# Operate the 1Password Kubernetes Operator

The homelab uses the official Helm chart named `connect`, but 1Password Connect is disabled. Each cluster runs the first-party operator with direct service-account authentication and a cluster-isolated, read-only 1Password service account. Production checks for item changes hourly. Development uses a one-year ticker as an effective manual-refresh mode because operator 1.12.0 cannot disable its `time.NewTicker` with zero.

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

The verifier explicitly annotates its canary `OnePasswordItem` after editing the item, which triggers the watched resource to reconcile without waiting for periodic polling. To request the same item-scoped refresh during development diagnosis, update a non-secret annotation:

```bash
kubectl --kubeconfig /home/vscode/.kube/homelab-development.config \
  -n <namespace> annotate onepassworditem/<name> \
  homelab.petebeegle.com/refresh-request="$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
  --overwrite
kubectl --kubeconfig /home/vscode/.kube/homelab-development.config \
  -n <namespace> wait onepassworditem/<name> \
  --for=condition=Ready=True --timeout=10m
```

Do not delete and recreate a `OnePasswordItem` to force refresh; deletion also deletes its owned Secret.

## Monitoring and diagnosis

Grafana alerts after ten minutes when the operator Deployment is absent/unavailable or a `OnePasswordItem` is not Ready. Start diagnosis with:

```bash
kubectl get onepassworditems.onepassword.com -A
kubectl -n onepassword-system get helmrelease,deployment,pods
kubectl -n onepassword-system logs deployment/onepassword-connect-operator --since=30m
```

A 1Password outage prevents refresh but does not remove an existing generated Secret. Confirm existing workloads remain running while investigating. Do not delete a durable `OnePasswordItem` as a diagnostic step: deletion also deletes its generated Kubernetes Secret.

If many or all items fail together, inspect service-account rate limits before changing item IDs or rotating tokens. Resolve the production token through the authenticated bootstrap reference and inject it only into the subprocess:

```bash
OP_SERVICE_ACCOUNT_TOKEN='op://cluster bootstrap/onepassword-production-operator/credential' \
  op run -- op service-account ratelimit
```

The `account` read/write row is shared across service accounts. This account currently permits 1000 requests/day. Seventeen production items polled every five minutes would require about 4896 baseline reads/day; hourly production polling requires about 408. Development periodic polling is effectively disabled and refreshes are requested explicitly. If the account row reaches zero remaining, existing generated Secrets stay available, but item readiness cannot recover until the provider-reported reset time. A new service-account token does not bypass an exhausted account-wide limit.

Automatic production rotation can take up to one hour. For a planned urgent rotation, annotate only the affected `OnePasswordItem` as shown above, using the production kubeconfig, and verify its Ready condition, generated Secret resource version, and consumer rollout without printing values.

## Prepare dual-publish items

The repository contains 16 encrypted Secret files but 17 Secret objects because the Immich file contains both `immich-secrets` and `immich-postgres-user`. Create all 17 items in `cluster production`; use the inventory as the field-label contract:

```bash
jq -r '.items[] | [.item_title, (.keys | join(","))] | @tsv' \
  tools/onepassword/production_items.json
```

For each entry:

1. Create a Secure Note with the exact inventory title.
2. Leave the note body empty and add exactly the listed custom fields.
3. Populate every field with the current legacy Secret bytes. Preserve multiline content and trailing newlines exactly.
4. Do not add a URL, file attachment, or any other populated field.

Use the live `grafana/grafana-credentials` Secret as the source for that item because its committed SOPS document fails MAC validation. Handle recovered values only in a trusted local session or secure clipboard; do not paste values into chat, shell arguments, Git, logs, or evidence. The remaining live Secrets are also acceptable migration sources and align directly with byte-parity acceptance.

After all items exist, resolve and validate their metadata from an authenticated user session:

```bash
unset OP_SERVICE_ACCOUNT_TOKEN
python3 tools/onepassword/render_production_items.py \
  --vault 'cluster production' \
  --check-only
```

The command captures item JSON without displaying it. It fails on duplicate, missing, empty, or extra fields and on URLs/files. Once check-only passes, omit `--check-only` to write ID-only `OnePasswordItem` manifests. Review every generated `itemPath` to confirm it contains only vault/item IDs.

After GitOps reconciliation, prove all pairs without displaying values:

```bash
python3 tools/onepassword/validate_secret_parity.py \
  --kubeconfig /home/vscode/.kube/homelab-production.config
```

Do not delete a durable `OnePasswordItem` to retry generation. Its generated Secret is owned by the resource and is deleted with it.

## Rollback during foundation

All application consumers still use SOPS during the foundation phases. If the production operator cannot meet acceptance, leave `sops-age` and consumers untouched, suspend the `onepassword-operator` Flux Kustomization if needed for diagnosis, and revert the new foundation Git change. Remove only a disposable canary namespace whose ownership is certain.
