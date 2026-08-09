# Research: Jellyfin Helm Client Apply

## Decision

Set `upgrade.serverSideApply: disabled` and
`rollback.serverSideApply: disabled` on the Jellyfin HelmRelease. Do not set
force.

## Rationale

The live `rollingUpdate` field is API-defaulted and not owned by Helm's SSA field
manager, so null cannot delete it. A read-only full Helm 4 server dry-run with
client-side apply succeeds, and the equivalent strategic patch uses retainKeys
to leave only `strategy.type=Recreate`. Flux documents force as ignored during
SSA; replacement is unnecessary after SSA is disabled.

## Alternatives

- SSA plus null: failed twice in production.
- Force replacement: broader and unnecessary; held as a last resort.
- Live delete/patch: violates GitOps and production-first constraints.
