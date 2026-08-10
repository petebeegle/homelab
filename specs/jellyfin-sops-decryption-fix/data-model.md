# Data Model: Jellyfin SOPS Decryption Fix

## Flux Reconciliation

- Identity: `flux-system/app-jellyfin`
- Source path: `./kubernetes/apps/jellyfin`
- Decryption provider: `sops`
- Key source: `flux-system/sops-age`
- Desired state: Ready at the exact merged revision

## Shared OAuth Credential

- Jellyfin Secret identity: `jellyfin/jellyfin-secrets`
- Jellyfin key: `JELLYFIN_OAUTH_CLIENT_SECRET`
- Authentik Secret identity: `authentik/authentik-secrets`
- Authentik key: `JELLYFIN_OAUTH_CLIENT_SECRET`
- Invariant: decoded byte strings are identical and the Jellyfin bytes are not an SOPS envelope

No credential value, encoding, or hash is stored in this model or evidence.
