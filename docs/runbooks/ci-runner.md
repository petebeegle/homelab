# CI Runner

The self-hosted runner `homelab-dev` runs every job that touches the development
cluster (`dev-smoke`'s `smoke` job, `dev-cleanup`). It lives in **production**, so it
can test and restore development from outside. Why: [decisions](../decisions.md#changes-go-through-pull-requests-and-the-check-is-the-evidence).

| Piece | Where |
|-------|-------|
| Actions Runner Controller | `kubernetes/infra/controllers/arc`, namespace `arc-systems` (production) |
| Runner scale set, policy, 1Password items | `kubernetes/apps/ci-runner`, namespace `ci-runner` (production) |
| The account it acts as in development | `kubernetes/apps/dev-runner` (development): ServiceAccount `dev-runner`, its Roles, and the `dev-runner-token` Secret |
| How jobs get the development kubeconfig | `.github/actions/dev-kubeconfig`, from the file named by `DEV_CLUSTER_KUBECONFIG` |

One ephemeral runner pod at a time (`maxRunners: 1`); that is the lock that keeps
smoke runs from overlapping in the shared development cluster.

## What fences it

- **No production credentials.** `automountServiceAccountToken: false`, and the app
  grants no RBAC.
- **Development access is narrow.** The mounted kubeconfig is the `dev-runner`
  account: it can manage Flux GitRepositories and Kustomizations and read pods, and
  cannot read secrets, delete namespaces or change RBAC.
- **Egress is allow-listed.** `CiliumNetworkPolicy ci-runner-egress` denies everything
  except DNS, GitHub, `registry.npmjs.org`, development's API server
  (`192.168.30.170:6443`) and internal gateway (`192.168.30.225:443`). Production's
  gateways are Cilium's Envoy, so a request to a production route gets
  `403 Access denied` from Envoy, not the app. A job that needs a new host fails with
  a connection timeout; add the host to the policy deliberately.

## Check it

```sh
export KUBECONFIG=~/.kube/homelab-production.config
kubectl -n flux-system get kustomization arc app-ci-runner
kubectl -n ci-runner get onepassworditem,autoscalingrunnerset
kubectl -n arc-systems get pods     # controller and the homelab-dev listener
```

A queued job that never starts usually means the listener is not running or the
GitHub App item did not sync. `dev-heartbeat` goes red when nothing on the runner has
succeeded for 12 hours.

## Rotate the development credentials

The runner's development access is the `dev-runner-token` Secret in development,
copied into the "cluster production" vault as the Document item
`dev-runner-kubeconfig` (file name `kubeconfig`). To rotate:

1. Delete the Secret in development; Flux recreates it with a new token:
   `kubectl --kubeconfig ~/.kube/homelab-development.config -n dev-runner delete secret dev-runner-token`
2. Build a kubeconfig from it into an ignored path (server
   `https://192.168.30.170:6443`, the Secret's `ca.crt` and `token`), without
   printing it, and replace the 1Password document's file.
3. The operator refreshes the production Secret within its polling interval (one
   hour), or annotate the `dev-runner-kubeconfig` OnePasswordItem in `ci-runner` to
   refresh it now. The next runner pod mounts the new file.

The GitHub App credentials are the `github_arc` item in the same vault.
