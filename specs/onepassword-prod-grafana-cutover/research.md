# Research: Production Grafana Credential Cutover

## Consumer Boundary

**Decision**: Cut over only `grafana-credentials`; leave `grafana-env` on SOPS.

**Rationale**: `grafana-credentials` supplies Grafana admin access, the OAuth client secret, and Grafana Operator external access. `grafana-env` supplies the Discord webhook and belongs to the separately planned notification-delivery cutover.

**Alternatives considered**: Moving both Grafana Secrets would enlarge the smoke surface and combine interactive authentication with notification delivery.

## Atomic References

**Decision**: Change four references together: Helm admin Secret, Helm OAuth mount, Grafana external admin user, and Grafana external admin password.

**Rationale**: They consume one byte-identical credential family. Partial migration can leave Grafana running while breaking OAuth or dashboard management.

**Alternatives considered**: Moving only Helm references or only Grafana Operator references was rejected as an incomplete consumer cutover.

## Validation Environment

**Decision**: Use strict local rendering and live read-only parity before merge, followed by a GitOps post-merge production rollout and immediate revert on failure.

**Rationale**: The binding development runbook explicitly identifies monitoring/Grafana as a coverage gap. Development omits the monitoring stack and production credentials, so a representative development Grafana smoke does not exist.

**Alternatives considered**: Temporarily applying production Grafana credentials to development would violate credential isolation. Temporarily pinning production Flux to an unmerged branch would weaken GitOps review gating.

## Manual Acceptance

**Decision**: Require Authentik login plus a known dashboard with live data after automated health and operator checks pass.

**Rationale**: Anonymous route and health probes cannot prove OAuth secret use, authenticated sessions, data-source access, or real dashboard behavior.

**Alternatives considered**: Treating `/api/health` or pod readiness as sufficient was rejected because neither exercises the changed OAuth credential.

## Rollback

**Decision**: Revert only the Grafana reference commit and retain both legacy and generated Secrets.

**Rationale**: Reverting four names is fast, auditable, and does not disturb other migration consumers. Deleting the `OnePasswordItem` would also delete its generated Secret and is explicitly destructive.

**Alternatives considered**: Live patching or deleting/recreating the item was rejected because it bypasses GitOps or risks Secret deletion.
