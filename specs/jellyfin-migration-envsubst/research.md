# Research: Jellyfin Migration Envsubst

## Decision: Disable substitution for the script-bearing resource

Flux performs post-build substitution over the final YAML, including literal
shell text stored in ConfigMap data. The merged migration script contains both
ordinary shell expansions such as `${path}` and a nested removal expression,
`${source_file#${source_root}/}`. The nested form causes `bad substitution`;
ordinary forms may be replaced with empty values.

Use the documented resource annotation
`kustomize.toolkit.fluxcd.io/substitute: disabled` on only the generated
`jellyfin-config-migration` ConfigMap. This makes the ownership boundary
explicit: Flux owns Kubernetes manifest variables, while `/bin/sh` owns the
migration script's variables.

## Alternatives considered

- Escape every shell expression with `$${...}`: supported by Flux, but couples
  the standalone shell source to a templating transport and makes direct shell
  tests invalid until an extra decoding step occurs. Missing one expression can
  silently alter behavior.
- Rewrite the nested expansion only: resolves the immediate parser error but
  leaves ordinary shell expansions vulnerable to substitution.
- Disable post-build substitution for the whole Jellyfin application: rejected
  because `jellyfin-values` intentionally uses cluster variables.

## Validation decision

Run `flux build kustomization --dry-run --strict-substitute` with local inline
production variables, then select the generated ConfigMap and compare its
`migrate.sh` value with the repository source before executing the existing
safety suite. Unlike the lower-level `flux envsubst` command, the local
Kustomization build honors the per-resource substitution policy. Production
controller reconciliation is still required because the CLI is only a local
reproduction of the controller stage.

## Tooling decision

The focused Python test may use `kubectl` and `flux` subprocesses because both
are required operator tools and exercise the actual failed integration. GitHub
CI must install a pinned Flux CLI before running this focused test. No YAML
library dependency is introduced.
