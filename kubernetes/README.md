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
For reference: [SOPS](https://github.com/getsops/sops)

```shell
gpg --list-secret-keys "${KEY_NAME}"
```

Update the `.sops.yaml` configuration to reference this fingerprint for relevant secrets.


### Configure for flux
```shell
sudo gpg --export-secret-keys --armor "<fingerprint>" |
  kubectl create secret generic sops-gpg \
  --namespace=flux-system \
  --from-file=sops.asc=/dev/stdin
```

### Working with secrets

```shell
# Encrpyt a kubernetes secret
sops -i -e secret.yaml

# Decrypt a secret
sops secret.yaml
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
