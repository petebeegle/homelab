# Data Model: Production Grafana Credential Cutover

## Credential Pair

- Legacy Secret: `grafana/grafana-credentials`
- Generated Secret: `grafana/grafana-credentials-onepassword`
- Required keys: `admin-user`, `admin-password`, `oauth-client-secret`
- Precondition: identical key sets and bytes; generated item Ready=True
- Lifecycle: both remain present throughout cutover and rollback

## Consumer References

| Consumer | Purpose | Before | After |
| --- | --- | --- | --- |
| Grafana Helm admin configuration | Initial/admin credential | `grafana-credentials` | `grafana-credentials-onepassword` |
| Grafana Helm secret mount | OAuth client secret file | `grafana-credentials` | `grafana-credentials-onepassword` |
| Grafana external admin user | Dashboard Operator access | `grafana-credentials` | `grafana-credentials-onepassword` |
| Grafana external admin password | Dashboard Operator access | `grafana-credentials` | `grafana-credentials-onepassword` |

## Preserved Reference

- Grafana Helm environment Secret remains `grafana-env`.
- The `grafana-env-onepassword` mirror remains published but unconsumed in this implementation.

## State Transitions

1. `Legacy`: all four consumers use `grafana-credentials`.
2. `Preflight`: generated item Ready and full parity passes; no consumer change.
3. `Cutover pending`: merged desired state points four consumers to the generated Secret.
4. `Cutover healthy`: Flux applied, workload/operator/health checks pass, and manual authenticated smoke passes.
5. `Rolled back`: a revert restores all four legacy references; both Secret copies remain.
