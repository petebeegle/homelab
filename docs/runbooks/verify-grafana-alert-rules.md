# Verify Grafana Alert Rules

Use this after changing `GrafanaAlertRuleGroup` manifests.

1. Confirm Flux rendered the alert rule CRs in the Grafana namespace.

```bash
kubectl get grafanaalertrulegroups.grafana.integreatly.org -n grafana
kubectl describe grafanaalertrulegroup -n grafana <name>
```

2. Check Grafana Operator reconciliation.

```bash
kubectl get pods -n grafana-operator
kubectl logs -n grafana-operator "$(kubectl get deploy -n grafana-operator -o name | head -n1)" --since=15m
```

3. Check Grafana ruler state from inside the cluster or through a port-forward.

```bash
kubectl port-forward -n grafana svc/grafana 3000:80
curl -fsS -u "$GRAFANA_USER:$GRAFANA_PASSWORD" \
  http://127.0.0.1:3000/api/ruler/grafana/api/v1/rules | jq .
```

Expected result: the `proxmox`, `flux`, `valheim`, and `mimir` rule groups appear in the ruler output, and the `GrafanaAlertRuleGroup` resources report successful reconciliation.
