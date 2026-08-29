# Research: onepassword-dev-cutover

- Development overlays are required because cert-manager and certs shared paths are also used by production.
- Immich item resources belong in the branch overlay so Kustomize applies the dynamic branch namespace.
- A temporary namespaced `CiliumNetworkPolicy` allowing only the `kube-apiserver` entity is the reversible outage simulation; deleting an item or token is explicitly forbidden. Generic IP allowlists do not reliably preserve the operator's API watch after Cilium Service translation.
- Operator 1.12.0 cannot disable `time.NewTicker` with zero. Development uses the merged one-year interval. Metadata-only item annotations do not enqueue reconciliation, so the outage validator restarts the stateless operator pod to force startup reconciliation and observes NotReady/Ready recovery.
- Let's Encrypt staging is used for the disposable certificate to avoid production rate-limit impact.
