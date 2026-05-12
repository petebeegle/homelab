# Discord Alert Delivery Health

Use this runbook when Grafana alert state is healthy but Discord still shows stale or missing alert messages, or when the `pretty-discord-alerts` delivery failure alerts fire.

## Scope

- Treat Git as the source of truth for Grafana rules and routing.
- Use live-cluster checks only to confirm current state and delivery symptoms.
- Manual Discord message correction is operational cleanup. It is not a GitOps desired-state change and does not need a repository commit.

## Confirm Grafana Rule State

Check whether Grafana still believes the affected rules are firing.

```bash
kubectl get grafanaalertrulegroups.grafana.integreatly.org -n grafana
kubectl describe grafanaalertrulegroup -n grafana apps
kubectl describe grafanaalertrulegroup -n grafana observability
```

If needed, inspect the ruler API through a port-forward.

```bash
kubectl port-forward -n grafana svc/grafana 3000:80
curl -fsS -u "$GRAFANA_USER:$GRAFANA_PASSWORD" \
  http://127.0.0.1:3000/api/ruler/grafana/api/v1/rules | jq .
```

Expected result: the affected rule state is inactive or ok before treating Discord as the only stale surface.

## Sanity-Check Mimir Queries

Confirm the underlying alert expressions still evaluate as expected in Mimir. Use Grafana Explore or the Grafana Prometheus datasource and evaluate the exact expressions from the affected `GrafanaAlertRuleGroup`.

Useful delivery-health checks:

```promql
sum(increase(webhook_discord_send_total{status="failure"}[10m])) OR vector(0)
sum(increase(webhook_requests_total{status="discord_error"}[10m])) OR vector(0)
sum by (pod) (increase(webhook_discord_send_total{status="failure"}[10m]))
sum by (pod) (increase(webhook_requests_total{status="discord_error"}[10m]))
```

Expected result: app availability expressions are no longer firing, while any nonzero delivery-health result points at the relay or Discord webhook path.

## Check Relay Replicas

List the relay pods and confirm every replica is ready.

```bash
kubectl -n monitoring get deploy,rs,pods -l app=pretty-discord-alerts -o wide
kubectl -n monitoring describe deploy pretty-discord-alerts
kubectl -n monitoring get endpoints pretty-discord-alerts -o yaml
```

Check metrics per replica so one bad pod is not hidden by aggregate success from the others.

```bash
for pod in $(kubectl -n monitoring get pod -l app=pretty-discord-alerts -o name); do
  kubectl -n monitoring port-forward "$pod" 18080:8080 >/tmp/pretty-discord-alerts-port-forward.log 2>&1 &
  pf_pid=$!
  sleep 2
  echo "== $pod =="
  curl -fsS http://127.0.0.1:18080/metrics | grep -E 'webhook_(discord_send|requests)_total'
  kill "$pf_pid"
  wait "$pf_pid" 2>/dev/null || true
done
```

Expected result: failures are either absent or isolated to a specific replica that should be investigated with logs and events.

## Inspect Logs And Events

Review recent relay logs and Kubernetes events around the failure window.

```bash
kubectl -n monitoring logs deploy/pretty-discord-alerts --since=30m --tail=300
kubectl -n monitoring get events --sort-by=.lastTimestamp
kubectl -n grafana logs deploy/grafana --since=30m --tail=300
kubectl -n grafana get events --sort-by=.lastTimestamp
```

Look for Discord HTTP errors, webhook secret issues, DNS or connection failures, Grafana contact point errors, pod restarts, and readiness probe failures.

## Recover Discord-Only Stale Alerts

If Grafana and Mimir show the alert is recovered but Discord still shows a stale firing message:

1. Confirm the stale message is Discord-only by checking Grafana rule state and the source PromQL expression.
2. Confirm `pretty-discord-alerts` is no longer recording new `status="failure"` or `status="discord_error"` increments.
3. Manually correct or remove the stale Discord message if it is operationally confusing.
4. Record the manual correction in the incident notes or operational handoff, not in Git.

Do not change alert expressions, Flux state, or Kubernetes manifests solely to repair a stale Discord message.

## Escalate

Escalate when delivery failures continue after the relay is healthy and Grafana rule state is correct. Include the affected Grafana rule names, the Discord webhook failure metrics, relay logs, recent events, and whether failures are isolated to one `pretty-discord-alerts` replica.
