# Observability — Grafana / Loki / Mimir / Alloy

## Common issues

- **Mimir OOM:** Increase memory limits in HelmRelease values; reduce initial metric burst on restart
- **Loki ingestion errors:** Check storage backend (minio) connectivity and bucket permissions
- **No metrics in Grafana:** Verify Alloy is scraping targets; check discovery config in `config.alloy`
- **Alloy not forwarding:** Check `config.alloy` for correct Mimir/Loki endpoint URLs and auth

## Stack

- **Alloy** — metrics/logs collector (replaces Prometheus Agent + Promtail)
- **Mimir** — long-term metrics storage (Prometheus-compatible)
- **Loki** — log aggregation
- **Grafana** — dashboards + alert rules
