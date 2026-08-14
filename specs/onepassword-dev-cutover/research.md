# Research: onepassword-dev-cutover

- Development overlays are required because cert-manager and certs shared paths are also used by production.
- Immich item resources belong in the branch overlay so Kustomize applies the dynamic branch namespace.
- A namespaced deny-egress NetworkPolicy is the reversible outage simulation; deleting an item or token is explicitly forbidden.
- Operator 1.12.0 cannot disable `time.NewTicker` with zero. Development uses the merged one-year interval and resource annotation updates as explicit, item-scoped reconcile triggers.
- Let's Encrypt staging is used for the disposable certificate to avoid production rate-limit impact.
