---
id: ADR-0001
status: accepted
scope:
  - gitops
  - kubernetes
  - flux
authority: binding
created: 2026-05-09
last_verified: 2026-05-10
supersedes: []
superseded_by:
---

# Flux GitOps Source Of Truth

## Decision

Git is the source of truth for Kubernetes desired state. Production reconciliation starts at `kubernetes/clusters/production/`, and Flux applies shared infrastructure from `kubernetes/infra/` plus apps from `kubernetes/apps/`.

## Rationale

- Flux gives a reviewable, repeatable path from committed manifests to cluster state.
- Cluster-specific Flux Kustomizations keep dependency ordering explicit.
- `postBuild.substituteFrom` allows shared manifests to stay environment-neutral while `cluster-vars` supplies production values.

## Consequences

- Prefer repo changes over manual `kubectl` edits.
- Manual cluster changes are temporary break-glass actions and should be backfilled into Git if they should persist.
- New apps require both shared app manifests and a cluster-layer Flux Kustomization.

## Operational Notes

- Use `flux debug kustomization <name> --show-vars` when variable substitution is the suspected failure.
- Check upstream `dependsOn` entries before debugging a downstream Kustomization.
- After pushing, verify Kustomizations and HelmReleases are Ready.
