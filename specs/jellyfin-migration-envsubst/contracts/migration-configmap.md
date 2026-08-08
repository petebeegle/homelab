# Contract: Migration ConfigMap Across Flux Post-Build

Given the Jellyfin application Kustomization:

1. Kustomize generates `ConfigMap/jellyfin-config-migration` in namespace
   `jellyfin` with `migrate-config.sh` under `data.migrate.sh`.
2. The resource carries annotation
   `kustomize.toolkit.fluxcd.io/substitute: disabled`.
3. Strict Flux substitution completes successfully for the full render.
4. The post-substitution `data.migrate.sh` value is identical to the source
   file, including nested and default-value shell expansions.
5. `ConfigMap/jellyfin-values` remains eligible for normal Flux substitution.
6. The init container executes the preserved script without a transport-time
   decode or rewrite step.
