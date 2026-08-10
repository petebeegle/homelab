# Quickstart: Jellyfin SOPS Decryption Fix

1. Render the production root and assert `flux-system/app-jellyfin` has exactly `provider: sops` and `secretRef.name: sops-age`.
2. Render development and confirm it is unchanged relative to `origin/main`.
3. Decrypt the committed Jellyfin and Authentik fields into memory and print only equality status.
4. Assert the PR changes no Secret manifest, consumer, workload, blueprint, or development path.
5. Merge only after CI and review pass.
6. Reconcile the exact merge revision, require `app-jellyfin` Ready/applied at that revision, and compare live decoded bytes in memory.
7. Stop if the live Jellyfin bytes still begin `ENC[` or differ from Authentik.
