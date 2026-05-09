# MCP Tool Routing

## Status

Accepted.

## Decision

Route operational questions to the tool that owns the signal:

- Kubernetes tooling for Kubernetes resources, pods, logs, events, Flux CRDs, and HelmRelease or Kustomization health.
- Grafana tooling for metrics, log queries, dashboards, alert rules, and datasource checks.
- CLI as fallback for computed debug output not exposed by tools.

## Rationale

- Kubernetes status and Grafana telemetry answer different questions.
- Using the wrong tool produces misleading conclusions, especially for crashes versus metrics.
- Keeping CLI as fallback preserves reproducibility without making shell access the first choice.

## Consequences

- Do not query metrics through Kubernetes tooling.
- Do not diagnose pod crash state through Grafana alone.
- Prefer `flux debug ...` only when computed Flux output is needed.

## Operational Notes

- Use `flux debug kustomization <name> --show-vars` for substituted values.
- Use `flux debug helmrelease <name> -n <namespace> --show-values` for final Helm values.
- For pod health, inspect pod phase, conditions, events, and logs from Kubernetes.
