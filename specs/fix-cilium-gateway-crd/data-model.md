# Data Model: Gateway Recovery State

This implementation changes declarative infrastructure state rather than
application data.

## Gateway API Definition Set

**Fields**:

- Release: `v1.5.1`
- Required type: `backendtlspolicies.gateway.networking.k8s.io`
- Channel: standard
- Owner: shared `crds` Flux Kustomization

**Validation rules**:

- The resource must render exactly once from the shared CRD Kustomization.
- Each cluster entrypoint must activate the shared CRD path exactly once.
- The live CRD must serve `gateway.networking.k8s.io/v1`.
- Existing Gateway API definitions and TLSRoute channel selection remain intact.

## Gateway Certificate Synchronization

**Relationships**:

- Gateway listener references a certificate Secret in namespace `gateway`.
- Cilium Operator observes the Gateway and copies required material into
  `cilium-secrets`.
- Cilium agents publish the synchronized secret through SDS.
- Per-node Envoy processes use the SDS certificate for HTTPS listeners.

**State transition**:

```text
CRD missing -> Gateway controller disabled -> no copied secrets -> no Envoy cert
CRD present + operator discovery -> secret copied -> SDS update -> TLS ready
```

## Recovery Signal

**Fields**:

- HTTPS response for whoami
- TLS completion for OTLP hostname
- New Proxmox metric sample timestamp
- Synthetic smoke status
- Grafana active alert state

**Validation rules**:

- Resource readiness alone is insufficient.
- At least one exact HTTPS user-path request must complete.
- Telemetry recovery requires a new sample, not merely collector pod readiness.
