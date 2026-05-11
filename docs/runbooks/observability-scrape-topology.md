---
status: current
scope:
  - observability
  - alloy
  - metrics
last_verified: 2026-05-11
---

# Observability Scrape Topology

Alloy runs as a DaemonSet and tolerates the control-plane taint so one pod can run on every Kubernetes node. Pod logs are discovered independently from metrics and are scoped to the local node; together, the DaemonSet collects logs for all pods without requiring metrics annotations.

Metrics scraping is opt-in for workloads. Alloy scrapes services and pods only when they set `prometheus.io/scrape: "true"` and rewrites the target port from `prometheus.io/port` when present. Prefer annotated service scraping for shared exporters such as kube-state-metrics; kube-state-metrics pods are excluded from pod metrics scraping to avoid duplicate series.

Container and node resource metrics come from kubelet HTTPS endpoints through the Kubernetes API server proxy. Alloy uses its service account token and CA bundle to scrape per-node `/metrics/cadvisor` and `/metrics/resource`, which provide container metrics such as `container_memory_working_set_bytes`.
