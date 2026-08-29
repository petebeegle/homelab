# Feature Specification: 1Password Development Cutover

**Feature Branch**: `codex/onepassword-dev-cutover`
**Created**: 2026-08-10
**Status**: Approved
**Risk Tier**: high

## Human Gate Status

The user approved phase 4 in the original migration plan: switch development cert-manager and the Immich branch profile, prove disposable certificate issuance and Immich API smoke, and prove a simulated 1Password outage preserves generated Secrets and running workloads.

Clarification found no unresolved choice. Production resources and consumers remain out of scope; development uses its isolated vault and service account.

## User Story 1 - Development Certificate (P1)

Development certificate issuance uses the 1Password-generated Cloudflare token Secret.

**Acceptance**: A disposable staging Certificate reaches Ready and is cleaned up; the legacy SOPS Secret remains for rollback.

## User Story 2 - Immich Branch (P1)

The Immich branch profile consumes development-vault generated configuration and database Secrets.

**Acceptance**: Branch smoke with development base reconciliation reaches the exact Immich `/api/server/ping` path and cleans up.

## User Story 3 - Outage Retention (P1)

An operator can prove a temporary 1Password connectivity outage does not delete existing generated Secrets or interrupt running consumers.

**Acceptance**: A reversible deny-egress policy blocks an explicit item-scoped refresh; Secret identity/data and workload identity/readiness remain unchanged; cleanup plus a second explicit refresh restores operator reconciliation.

## Requirements

- **FR-001**: Git MUST contain only development vault/item IDs and exact non-secret schemas for three items.
- **FR-002**: Development cert-manager/certs MUST reference `cloudflare-api-token-onepassword`; production MUST remain unchanged.
- **FR-003**: The Immich branch overlay MUST reference `immich-secrets-onepassword` and `immich-postgres-user-onepassword` throughout.
- **FR-004**: All three generated Secrets MUST be Ready and byte-identical to their legacy development source before consumer validation.
- **FR-005**: SOPS resources/decryption MUST remain available for reference rollback.
- **FR-006**: Certificate, Immich API, and outage-retention tests MUST suppress credential data and clean up temporary resources.
- **FR-007**: Outage simulation MUST NOT delete the service-account token or any `OnePasswordItem`.

## Success Criteria

- **SC-001**: Three development items report Ready and 3/3 parity.
- **SC-002**: Disposable staging certificate issuance passes.
- **SC-003**: Immich branch API smoke passes with exact branch/base revision evidence.
- **SC-004**: An explicit refresh fails during the simulated outage while the generated Secret and workload remain available, then succeeds after cleanup.
- **SC-005**: Production render and Secret references are unchanged.

## Assumptions

- The user can create three exact Secure Note items in `cluster development`.
- Current development SOPS bytes are the initial value authority.
- The temporary outage policy is limited to the operator Deployment and removed in a guaranteed cleanup path.
- Development periodic refresh is effectively disabled by the merged one-year interval; annotation updates explicitly request reconciliation.

## Open Questions

- None.
