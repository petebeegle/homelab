# Feature Specification: Jellyfin SOPS Decryption Fix

**Feature Branch**: `codex/jellyfin-sops-decryption-fix`
**Created**: 2026-08-10
**Status**: Approved
**Risk Tier**: high
**Input**: Correct production Jellyfin's missing SOPS reconciliation before 1Password dual-publication parity.

## Human Gate Status

**Intent Brief**: During the approved 1Password migration, the user confirmed that the decoded live Jellyfin OAuth client-secret value is SOPS ciphertext. Inspection proved the production Jellyfin Flux resource lacks decryption while the committed Jellyfin and Authentik fields decrypt to identical plaintext. The user explicitly approved a separate prerequisite PR to correct this without exposing values.

**Clarify Status**: Completed with no questions; the affected resource, authority, scope, rollback, and no-output acceptance are explicit.

**Spec Gate**: Approved by the user in conversation on 2026-08-10.

## Summary

Restore the intended production secret behavior so Jellyfin receives the actual shared OAuth client secret rather than committed ciphertext. Preserve the encrypted manifest, consumer reference, Authentik configuration, and every other application path.

## Binding Sources

- `AGENTS.md`
- `.specify/memory/constitution.md`
- `docs/decisions/sops-age-secrets.md`
- `docs/decisions/tdd-and-development-smoke-evidence.md`
- `docs/runbooks/implementation-workflow.md`
- `docs/runbooks/jellyfin-authentik-sso.md`

## Scope

### In Scope

- Configure the production `app-jellyfin` reconciliation to decrypt SOPS resources using the existing `flux-system/sops-age` Secret.
- Prove the committed Jellyfin and Authentik OAuth values decrypt to identical bytes without displaying either value.
- After merge, prove Flux fetched/applied the exact revision and the live decoded Jellyfin and Authentik Secret bytes are identical without displaying either value.

### Out Of Scope

- Editing or re-encrypting either SOPS Secret manifest.
- Changing the Jellyfin or Authentik Secret name, key, consumer, OAuth provider, or workload definition.
- Switching any consumer to 1Password; that remains in later migration phases.
- Rotating the OAuth client secret.

## User Scenarios & Testing

### User Story 1 - Restore Jellyfin OAuth Secret Reconciliation (Priority: P1)

As the homelab operator, I need production Jellyfin to receive the same plaintext OAuth client secret configured in Authentik so SSO configuration is coherent and the 1Password migration can prove byte parity.

**Why this priority**: This is the only defect and blocks the dual-publish parity gate.

**Independent Test**: Render the production cluster, verify the Flux resource contains SOPS decryption with `sops-age`, and compare committed plus post-merge live bytes in memory with status-only output.

**Acceptance Scenarios**:

1. **Given** the encrypted Jellyfin Secret and existing Age key, **When** `app-jellyfin` reconciles, **Then** the live Secret contains plaintext equal to the Authentik Jellyfin OAuth field rather than an `ENC[` envelope.
2. **Given** the fix is reviewed, **When** the diff is inspected, **Then** only the production Flux reconciliation resource, its generated architecture description, and SDD evidence change; secret documents and consumers do not.
3. **Given** reconciliation cannot decrypt, **When** Flux reports failure, **Then** acceptance stops and rollback is removal of the added decryption stanza through Git.

## Requirements

- **FR-001**: Production `app-jellyfin` MUST use Flux SOPS decryption with Secret reference `sops-age`.
- **FR-002**: Both committed encrypted Secret manifests and all consumer references MUST remain byte-for-byte unchanged.
- **FR-003**: Local validation MUST prove the two committed fields decrypt to identical bytes without printing values.
- **FR-004**: Post-merge validation MUST prove exact fetched/applied revision and live Secret byte equality without printing values, Base64, or hashes.
- **FR-005**: The change MUST NOT create, rotate, or otherwise alter credential material.
- **FR-006**: Failure or mismatch MUST block the dual-publish PR from reaching its parity gate.

## Edge Cases

- A missing or invalid Age key causes Flux reconciliation failure and blocks acceptance.
- A live Jellyfin value that still begins `ENC[` after reconciliation is a failed deployment even if the Kustomization reports Ready.
- Different plaintexts between Jellyfin and Authentik block acceptance and require credential-source investigation; neither is silently overwritten.

## Risk And Validation Expectations

This is high-risk secret-handling work. The changed Flux resource exists only in the production cluster path, while development Jellyfin uses a branch placeholder rather than this production SOPS Secret. A development-cluster mutation would therefore not exercise the changed resource and could introduce production credential material into development. Acceptance uses local encrypted-manifest equality, strict render/policy checks, normal PR review, and exact-revision post-merge production reconciliation with no-output live comparison.

## Success Criteria

- **SC-001**: Production rendering shows exactly one SOPS decryption configuration on `app-jellyfin` referencing `sops-age`.
- **SC-002**: No Secret manifest, OAuth consumer, Authentik blueprint, or Jellyfin workload file changes in the PR; generated architecture records only that Jellyfin now uses SOPS.
- **SC-003**: Status-only local comparison reports committed plaintext equality.
- **SC-004**: Status-only post-merge comparison reports live equality and confirms the Jellyfin value is not an `ENC[` envelope.

## Assumptions

- The existing production `sops-age` Secret is healthy because other production Kustomizations decrypt with it.
- The encrypted Jellyfin and Authentik values intentionally represent the same shared OAuth client secret, as confirmed by local no-output comparison.

## Open Questions

- None.
