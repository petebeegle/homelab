# Observability: Grafana, Loki, Mimir, Alloy

## Research Resources

1. **Grafana docs:** https://grafana.com/docs/
2. **Loki setup:** https://grafana.com/docs/loki/latest/setup/
3. **Mimir setup:** https://grafana.com/docs/mimir/latest/
4. **Alloy (collector):** https://grafana.com/docs/alloy/latest/
5. **Recommended:** Use Kubernetes Monitoring Helm chart for unified setup

## Troubleshooting

**Prefer `homelab-mcp` tools** over CLI commands:
- Use `cluster_health` to check for problem pods and PVC issues in monitoring namespace
- Use `pod_logs(namespace="monitoring", label="app.kubernetes.io/name=grafana")` for Grafana logs
- Use `pod_logs(namespace="monitoring", label="app.kubernetes.io/name=loki")` for Loki logs
- Use `pod_logs(namespace="monitoring", label="app.kubernetes.io/name=mimir")` for Mimir logs
- Use `pod_logs(namespace="monitoring", label="app.kubernetes.io/name=alloy")` for Alloy logs
- Use `helmrelease_debug(name=<name>, namespace="monitoring")` to deep-dive a monitoring HelmRelease

**Common issues:**
- Mimir OOM: Increase limits, reduce initial metric burst on restart
- Loki ingestion errors: Check storage backend (minio) connectivity
- No metrics in Grafana: Verify Alloy is scraping targets, check discovery config
- Alloy not forwarding: Check `config.alloy` for correct endpoint URLs
