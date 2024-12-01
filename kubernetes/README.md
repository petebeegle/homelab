# My Cluster Flux

What is it? How is it? Read on.

## Structure

```sh
kubernetes
├── apps # Non-Infra manifests. Things like homepage or podinfo
│   ├── base # Base-level app configs shared by all clusters
│   │   ├── app1
│   │   │   └── kustomization.yaml
│   │   └── app2
│   │       └── kustomization.yaml
│   └── production # Cluster-specific configs. This is the entrypoint from a cluster perspective
│       └── kustomization.yaml
├── clusters
│   └── production
│       ├── apps.yaml # Notifies flux to check the `kubernetes/apps` directory
│       ├── flux-system # Flux stuff, it's impossible to know what goes on here
│       │   └── kustomization.yaml
│       └── infrastructure.yaml # Defines Kustomizations for each infrastructure manifest
├── infrastructure # Important stuff goes here, like load balances, networking, etc.
│   ├── infra1
│   |   └── kustomization.yaml
│   └── infra2
│       └── kustomization.yaml
└── README.md # You are here
```

## Creating Secrets
For reference: [SOPS](https://github.com/getsops/sops), [age](https://github.com/FiloSottile/age)

Update the `.sops.yaml` configuration to reference this fingerprint for relevant secrets.


### Configure for flux
```shell
cat ~/.config/sops/age/keys.agekey |
  kubectl create secret generic sops-age \
  --namespace=flux-system \
  --from-file=keys.agekey=/dev/stdin
```

### Working with secrets

```shell
# Encrpyt a kubernetes secret
sops -i -e secret.yaml

# Decrypt a secret
sops secret.yaml
```

## Depdendency Management

I use renovate, it runs as a cronjob in the `renovate` namespace.

You can run it manually as well if you need:
```sh
kubectl create job --from=cronjob.batch/renovate renovate-manual-run -n renovate
```

Run it locally with dry-run enabled:
```sh
docker run \
    --rm \
    -e LOG_LEVEL="debug" \
    -e RENOVATE_CONFIG="$(cat renovate.json)" \
    renovate/renovate:39.42.4 \
    --token "$TOKEN" \
    --dry-run="true" \
    petebeegle/homelab
```

## Helpful commands for people with small memories

```sh
# view logs
flux logs -f

# watch kustomization events
flux get kustomizations --watch

# get the helm releases
kubectl get helmreleases -n kube-system

# get helm repositories 
kubectl get helmrepositories -n kube-system
```
