---
name: observability
description: Grafana, Loki, Mimir, and Alloy reference for this homelab. Invoke when troubleshooting the monitoring stack, missing metrics, log ingestion issues, Alloy scraping problems, or when working with dashboards and alerts. Also invoke to clarify which MCP tool to use for observability questions.
---

## Tool Priority

1. `grafana` MCP — query metrics, inspect dashboards, check alert rules and datasources
2. `kubernetes` MCP — pod logs, HelmRelease conditions/events, PVC and pod health in `monitoring` namespace
3. CLI — fallback only

Use `grafana` MCP when the question is about data *inside* Grafana (metrics, dashboards, alerts).
Use `kubernetes` MCP when the question is about the *health of the monitoring stack itself* (pods crashing, HelmRelease failures, PVCs).

## Common Issues

- Mimir OOM: Increase limits, reduce initial metric burst on restart
- Loki ingestion errors: Check storage backend (minio) connectivity
- No metrics in Grafana: Verify Alloy is scraping targets, check discovery config
- Alloy not forwarding: Check `config.alloy` for correct endpoint URLs

## Research Resources

1. **Grafana docs:** https://grafana.com/docs/
2. **Loki setup:** https://grafana.com/docs/loki/latest/setup/
3. **Mimir setup:** https://grafana.com/docs/mimir/latest/
4. **Alloy (collector):** https://grafana.com/docs/alloy/latest/
5. **Recommended:** Use Kubernetes Monitoring Helm chart for unified setup
