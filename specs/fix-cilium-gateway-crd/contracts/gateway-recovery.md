# Gateway Recovery Contract

## Declarative Contract

`kubernetes/infra/crds` must render exactly one CustomResourceDefinition named
`backendtlspolicies.gateway.networking.k8s.io` from Gateway API v1.5.1. Both
`kubernetes/clusters/development` and `kubernetes/clusters/production` must
render exactly one Flux activation of `./kubernetes/infra/crds`.

## HTTPS Contract

For a valid hostname attached to the internal Gateway:

- TCP port 443 accepts a connection.
- TLS negotiation returns a certificate rather than resetting the connection.
- The routed request returns an HTTP response below 500.

Primary probes:

- Development: `https://whoami.dev.lab.petebeegle.com`
- Production: `https://whoami.lab.petebeegle.com`
- Telemetry: `https://otel.lab.petebeegle.com`

## Control-Plane Contract

- Cilium Operator starts without a missing-required-Gateway-API-resource error.
- Gateway certificate material exists in `cilium-secrets`.
- Envoy reports one or more configured certificates.
- Existing Gateway and Route resources are not rewritten by this implementation.

## Observability Contract

- Proxmox metric series receive timestamps newer than the recovery deployment.
- The next synthetic smoke execution does not report shared TLS resets.
- Outage-derived alerts resolve from recovered signals; rules are not silenced or
  weakened.
