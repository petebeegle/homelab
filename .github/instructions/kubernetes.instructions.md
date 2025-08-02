# GitHub Copilot Custom Instructions for Kubernetes

applyTo:
  - kubernetes/**
  - kubernetes/**/*

## What does this part of the repository do?
This directory manages Kubernetes infrastructure and workloads for the homelab, using Kustomize overlays, Helm (for upstream charts), Cilium, Gateway API, OpenTelemetry, Prometheus, Grafana, and Loki. It implements GitOps, secure infrastructure as code, and cloud-native observability.

## What coding style, best practices, or architectural patterns should GitHub Copilot follow?
- Use minimal, composable, and secure manifests. Prefer overlays with Kustomize for environment-specific configuration.
- Use Helm only for upstream charts; otherwise, prefer native YAML and Kustomize overlays.
- Namespace resources appropriately and use labels/annotations for observability and GitOps.
- Integrate Cilium for networking, Gateway API for ingress, and enable OpenTelemetry, Prometheus, Grafana, and Loki for observability.
- Use SOPS for secrets and never hardcode sensitive data.
- All manifests must be idempotent, declarative, and production-grade.
- Follow GitOps best practices (Flux) and automate deployments where possible.
- Reference `/kubernetes/infra/` for infra, `/kubernetes/apps/` for workloads, and use overlays for production/staging.

## What should GitHub Copilot avoid?
- Avoid monolithic or overly complex manifests and scripts.
- Avoid hardcoding secrets or sensitive data.
- Avoid non-declarative or imperative configuration unless explicitly required.
- Avoid ignoring project conventions or structure.

## Additional context
- All code and configuration should be production-grade, secure, and maintainable.
- When in doubt, explain your reasoning and reference relevant project conventions.

_Last updated: 2025-08-02_
