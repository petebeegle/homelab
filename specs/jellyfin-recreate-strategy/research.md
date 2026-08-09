# Research: Jellyfin Recreate Strategy

## Decision: Emit an explicit null for rollingUpdate

The existing Deployment is `RollingUpdate` and carries
`spec.strategy.rollingUpdate`. Chart 3.2.0 directly renders the
`deploymentStrategy` values map. Rendering only `type: Recreate` leaves the old
field present during Helm controller server-side apply, producing an invalid
merged object. Adding `rollingUpdate: null` renders an explicit clear operation
alongside `type: Recreate`.

## Alternatives considered

- Force-recreate the Deployment: rejected because it is a live-cluster-first
  mutation and bypasses reviewable GitOps desired state.
- Temporarily retain RollingUpdate: rejected because the binding migration
  design requires single-writer `Recreate` behavior.
- Change field ownership or force Helm apply: broader and riskier than declaring
  the intended field removal in the chart values.

## Validation decision

Template Jellyfin chart `3.2.0` with the repository values and assert the
Deployment strategy contains `rollingUpdate: null` and `type: Recreate` in the
same mapping. Continue running the full config migration test suite and verify
production controller acceptance after merge.
