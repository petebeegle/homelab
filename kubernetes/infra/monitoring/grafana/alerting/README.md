# Grafana Alerting Configuration

This directory contains Grafana Unified Alerting configuration as code.

## Structure

```
alerting/
├── policies.yaml           # Notification routing policies
└── rules/                  # Alert rules organized by category
    ├── kubernetes-pods.yaml        # Pod health (crashes, not ready, pending)
    ├── kubernetes-resources.yaml   # Resource usage (CPU, memory, PVC)
    └── infrastructure.yaml         # Node health (not ready, pressure)
```

## How It Works

1. **ConfigMaps**: Each YAML file is a ConfigMap containing Grafana provisioning config
2. **Mounted into Grafana**: The HelmRelease mounts these into `/etc/grafana/provisioning/alerting/`
3. **Auto-loaded**: Grafana automatically loads provisioning files on startup
4. **GitOps**: Changes are deployed via FluxCD when committed to git

## Notification Flow

All alerts follow this path:
1. **Alert Rule** triggers based on Prometheus query
2. **Notification Policy** (`policies.yaml`) groups and routes to contact point
3. **Contact Point** (`app.yaml` - Discord webhook) sends notification

## Adding New Alert Rules

### Option 1: Add to Existing Category

Edit the appropriate file in `rules/`:
- Pod issues → `kubernetes-pods.yaml`
- Resource limits → `kubernetes-resources.yaml`
- Node/cluster issues → `infrastructure.yaml`

### Option 2: Create New Category

1. Create `rules/new-category.yaml`:
```yaml
---
apiVersion: v1
kind: ConfigMap
metadata:
  name: grafana-alert-rules-new-category
  namespace: monitoring
  labels:
    grafana_alert: "rules"
data:
  new-category.yaml: |
    apiVersion: 1
    groups:
      - name: new-category
        folder: NewFolder
        interval: 1m
        orgId: 1
        rules:
          - uid: unique-alert-id
            title: Alert Title
            condition: C
            data:
              - refId: A
                datasourceUid: prometheus
                model:
                  expr: up == 0  # Your PromQL query
              - refId: C
                datasourceUid: __expr__
                model:
                  expression: A
                  type: threshold
            for: 5m
            annotations:
              description: "Detailed description"
              summary: Short summary
            labels:
              severity: warning
```

2. Add to `rules/kustomization.yaml`:
```yaml
resources:
  - new-category.yaml
```

3. Mount in `app.yaml` under `extraConfigmapMounts`:
```yaml
- name: alerting-rules-new-category
  mountPath: /etc/grafana/provisioning/alerting/rules-new-category.yaml
  subPath: new-category.yaml
  configMap: grafana-alert-rules-new-category
  readOnly: true
```

## Alert Rule Reference

### Datasource UIDs
- `prometheus` - Mimir datasource (metrics)
- `loki` - Loki datasource (logs)
- `__expr__` - Built-in expressions (thresholds, math)

### Severities
- `critical` - Immediate attention required
- `warning` - Needs attention soon
- `info` - FYI only

### Common PromQL Queries

**Pod restarts:**
```promql
rate(kube_pod_container_status_restarts_total[5m]) > 0
```

**Memory usage:**
```promql
(container_memory_working_set_bytes / container_spec_memory_limit_bytes) * 100 > 90
```

**CPU usage:**
```promql
rate(container_cpu_usage_seconds_total[5m]) > 0.9
```

**PVC usage:**
```promql
(kubelet_volume_stats_used_bytes / kubelet_volume_stats_capacity_bytes) * 100 > 85
```

## Adding New Contact Points

Edit `app.yaml` under `values.alerting.contactpoints.yaml` to add Slack, PagerDuty, etc.

## Testing Alerts

```bash
# Force reconcile to apply changes
flux reconcile helmrelease grafana -n monitoring

# Check Grafana logs for provisioning errors
kubectl logs -n monitoring -l app.kubernetes.io/name=grafana | grep -i alert

# Trigger test alert (creates firing alert)
kubectl run test-crashloop --image=busybox --restart=Never -- /bin/sh -c "exit 1"
```

## Troubleshooting

**Alerts not showing in Grafana:**
- Check ConfigMaps exist: `kubectl get cm -n monitoring | grep grafana-alert`
- Check mounts: `kubectl describe pod -n monitoring -l app.kubernetes.io/name=grafana`
- Check Grafana logs: `kubectl logs -n monitoring -l app.kubernetes.io/name=grafana`

**Datasource UID errors:**
- In Grafana UI, go to Connections → Data sources
- Click on Prometheus datasource, copy the UID from URL
- Update `datasourceUid` in alert rules if needed

**Alerts not firing:**
- Verify PromQL query returns data in Grafana Explore
- Check `for` duration (alert must be true for this long)
- Review notification policy matching in Grafana UI
