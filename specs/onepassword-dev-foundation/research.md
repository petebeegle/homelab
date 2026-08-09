# Research: onepassword-dev-foundation

## Direct Operator Authentication

**Decision**: Use the first-party 1Password Operator with a 1Password service-account token and no Connect server.

**Rationale**: Operator 1.12.0 supports `OP_SERVICE_ACCOUNT_TOKEN` directly, exposes `OnePasswordItem` Ready status, and supports automatic Deployment restarts. This preserves the user's first-party integration choice with one controller and one bootstrap token.

**Alternatives considered**: 1Password Connect plus the operator adds API/sync workloads and two bootstrap credentials; External Secrets Operator is broader but not the approved first-party controller.

## Official Chart Packaging

**Decision**: Reconcile official chart `connect` 2.4.1 with `connect.create=false`, `operator.create=true`, and `operator.authMethod=service-account`.

**Rationale**: The chart is the maintained install surface for the operator even when its namesake Connect component is disabled. Pinning chart/operator versions avoids unreviewed controller changes.

**Alternatives considered**: Vendoring generated controller YAML would increase update and provenance maintenance; tracking `latest` would violate deterministic GitOps expectations.

## Bootstrap Trust Root

**Decision**: Add explicit `sops`, `dual`, and `onepassword` modes to a reusable bootstrap-secret helper. Default to `sops`; development selects `dual` in this phase.

**Rationale**: Existing clusters and production remain safe while development gains the new trust root. Only the non-secret `op://` reference enters Terraform configuration. The resolved token flows from `op read` to a mode-0600 temporary file and then `kubectl --from-file`.

**Alternatives considered**: A Terraform sensitive variable would place the token in Terraform state; a committed encrypted token would retain SOPS as the new system's trust root; a local token file would recreate the static workstation-key model.

## Canary Validation

**Decision**: Keep canary manifests out of the live cluster entrypoint and apply them temporarily through a dedicated verifier that resolves item IDs from `op`.

**Rationale**: Vault/item IDs are external state and the canary is validation rather than durable service state. Temporary application follows the development smoke model and cleans up by default.

**Alternatives considered**: Committing placeholder IDs would break Flux; a permanent canary adds unnecessary standing credential and workload; readiness-only validation would not prove rotation/restart behavior.

## CLI Tooling

**Decision**: Pin 1Password CLI 2.35.0 in the devcontainer and verify the downloaded Linux amd64 archive with SHA-256 `4457ade59850b852c64c77164235b34dd0b984ef7826eb0ccd32f1fd78a2ceb7`.

**Rationale**: This is the current stable CLI release as of 2026-08-01 and makes the bootstrap/smoke environment deterministic.

**Alternatives considered**: An unpinned apt install is easier but non-reproducible; a host-only CLI makes the documented devcontainer workflow incomplete.
