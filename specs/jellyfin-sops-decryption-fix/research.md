# Research: Jellyfin SOPS Decryption Fix

## Root Cause

**Decision**: Treat the missing `spec.decryption` on the production `app-jellyfin` Flux Kustomization as the defect.

**Rationale**: The encrypted manifest is included by the reconciled app path, but the cluster-layer Kustomization lacks decryption. The live decoded Secret therefore contains the literal `ENC[AES256_GCM,...]` envelope. Other production SOPS-backed apps use `provider: sops` with `secretRef.name: sops-age`.

**Alternatives considered**: Copying the live Jellyfin ciphertext into 1Password was rejected because it perpetuates the defect. Editing or re-encrypting the Secret was rejected because the committed plaintext is already correct.

## Credential Authority

**Decision**: Require the Jellyfin and Authentik committed plaintexts, then live Secret bytes, to match without output.

**Rationale**: Jellyfin and the Authentik provider consume the same OAuth client secret. A local in-memory SOPS comparison already proved the committed values match.

**Alternatives considered**: Hash logging was rejected because hashes of credentials are unnecessary evidence. Rotation was rejected as out of scope.

## Validation Environment

**Decision**: Use a documented development exception and exact-revision production verification after merge.

**Rationale**: The changed resource exists only under `clusters/production`; development Jellyfin uses a non-secret placeholder branch profile. Reusing the production credential in development would weaken cluster isolation without exercising the changed Flux resource.

**Alternatives considered**: Applying the production Kustomization to development was rejected because it would reconcile production app paths and credentials into the wrong cluster.
