---
id: ADR-0014
status: accepted
scope:
  - observability
  - grafana
  - metrics
  - logs
authority: binding
created: 2026-05-16
last_verified: 2026-05-16
supersedes: []
superseded_by:
---

# Observability Stack

## Decision

The observability stack is managed through GitOps. Durable changes to Grafana, Mimir, Loki, Alloy, kube-state-metrics, dashboards, alert rules, and alert delivery are made in this repository and reconciled by Flux.

Grafana is the user-facing observability UI. Grafana datasources, contact points, and notification policies are configured from the Grafana HelmRelease. Dashboards, folders, and alert rules are owned through Grafana Operator custom resources where the repository uses those CRs.

Mimir is the Prometheus-compatible metrics backend and is exposed to Grafana through datasource UID `prometheus`. Loki is the log backend and is exposed to Grafana through datasource UID `loki`.

Alloy is the cluster collector for metrics and logs. Workload metrics scraping is opt-in with `prometheus.io/scrape: "true"` annotations on services or pods, with `prometheus.io/port` and `prometheus.io/path` used when present. Pod logs are collected independently of metrics annotations. Alloy also scrapes kubelet resource and cAdvisor metrics through the Kubernetes API server proxy for node and container resource telemetry.

kube-state-metrics provides Kubernetes state metrics and, where configured, custom resource state metrics for Flux, Gateway API, and cert-manager resources.

Grafana alerting and dashboards are GitOps-managed. Alert delivery to Discord goes through `pretty-discord-alerts`, which formats and relays Grafana webhook notifications.

Grafana is exposed through Gateway API as `monitoring.${cluster_domain}` on the internal and external HTTPS Gateway listeners.

## Rationale

- GitOps keeps observability configuration reviewable, repeatable, and aligned with the rest of the cluster desired state.
- Grafana gives operators one primary place to inspect dashboards, logs, metrics, and alert state.
- Stable datasource UIDs let dashboards and alert rules refer to Mimir and Loki without depending on display names or generated identifiers.
- Alloy keeps collection behavior centralized while annotations let workloads opt in to metrics scraping only when they intentionally expose metrics.
- kube-state-metrics custom resource state metrics make Flux, Gateway API, and certificate health queryable from the same Prometheus-compatible backend as workload and node metrics.
- `pretty-discord-alerts` separates Grafana alert evaluation from Discord-specific formatting and delivery concerns.
- Gateway API exposure follows the repository ingress pattern and avoids introducing traditional Ingress resources.

## Consequences

- Observability changes should be made as repository changes first, with live-cluster edits limited to temporary investigation or repair.
- New dashboards and alert rules should use the existing Grafana Operator custom resource patterns when they belong in Git.
- PromQL-based dashboards and alerts should use datasource UID `prometheus`; LogQL-based dashboards and alerts should use datasource UID `loki`.
- Workloads that need metrics scraping must add the expected Prometheus annotations to a service or pod.
- Alert delivery troubleshooting must consider both Grafana alert state and the `pretty-discord-alerts` relay.
- This decision records existing repository behavior and does not require live-cluster changes.

## Operational Notes

- Use `docs/runbooks/observability-scrape-topology.md` for the operational scrape topology.
- Use `docs/runbooks/verify-grafana-alert-rules.md` after changing `GrafanaAlertRuleGroup` manifests.
- Use `docs/runbooks/discord-alert-delivery-health.md` when Grafana alert state and Discord delivery disagree.
- Gateway exposure for Grafana is defined in `kubernetes/infra/monitoring/grafana/gateway.yaml`.
