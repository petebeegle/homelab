# Quickstart: Validate Cilium Gateway Recovery

## Prerequisites

- Work on branch `codex/fix-cilium-gateway-crd`.
- Development and production kubeconfigs are available at their documented paths.
- Flux and kubectl are installed.
- The implementation branch may be pushed for development reconciliation.

## Local Render

Render the shared CRDs and each cluster entrypoint. Assert that
`backendtlspolicies.gateway.networking.k8s.io` appears exactly once in the shared
CRD output and `./kubernetes/infra/crds` appears exactly once in each cluster
output, then run the architecture check.

## Development

Run the whoami verifier with the shared base enabled:

```bash
python3 tools/development/verify_branch_deploy.py \
  --app whoami \
  --branch codex/fix-cilium-gateway-crd \
  --slug fix-cilium-gateway-crd \
  --push \
  --include-cluster-base
```

Confirm the CRD exists, Cilium Operator no longer reports a missing required
Gateway API resource, synced certificate material exists, and the exact whoami
HTTPS URL completes without a TLS reset. If startup discovery remains stale,
restart only the development Cilium Operator and repeat these checks.

## Production Follow-Up

After merge, wait for Flux to fetch and apply the merge SHA. Confirm the live CRD
and restart only the Cilium Operator if needed for startup discovery. Verify:

1. `cilium-secrets` contains the gateway certificate copies.
2. Envoy reports configured certificates.
3. Whoami and OTLP HTTPS handshakes complete.
4. A new Proxmox metric sample arrives.
5. The scheduled synthetic run succeeds and outage-derived alerts resolve.

Record exact commands, timestamps, SHAs, and results in `evidence.md`.
