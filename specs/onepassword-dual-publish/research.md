# Research: onepassword-dual-publish

## Resource count

**Decision**: Migrate 17 Secret resources represented by 16 encrypted files.

**Evidence**: `kubernetes/apps/immich/base/secret.yaml` contains two `kind: Secret` documents. Live API metadata confirms both and their distinct schemas.

## Field mapping

**Decision**: Use empty Secure Notes with exact non-empty custom field labels.

**Evidence**: Official operator source `BuildKubernetesSecretData` converts non-empty item fields to Secret data by field label, preserves labels already valid under Kubernetes `[-._a-zA-Z0-9]+`, skips empty values, and accepts a `OnePasswordItem.type`. Dotted and uppercase inventory keys are therefore supported. Extra populated built-ins would become extra Secret keys and are rejected by the resolver.

## Production-only placement

**Decision**: Keep all application items in a production cluster path and reconcile them through one production Flux Kustomization after namespace owners.

**Rationale**: Shared app paths are also used by development branch validation. A production item ID there would be unreadable by the isolated development service account.

## Value recovery

**Decision**: Treat live Kubernetes Secrets as the byte authority for initial item population and parity; specifically require live recovery for Grafana credentials.

**Rationale**: This avoids stale source assumptions and handles the confirmed Grafana SOPS MAC mismatch. Tooling never prints or persists values.
