---
id: ADR-0003
status: accepted
scope:
  - secrets
  - sops
  - age
authority: binding
created: 2026-05-09
last_verified: 2026-05-10
supersedes: []
superseded_by:
---

# SOPS Age Secrets

## Decision

Kubernetes secrets committed to the repo must be encrypted with SOPS using Age recipients. Flux decrypts them in-cluster with the `sops-age` Secret in `flux-system`.

## Rationale

- Secrets stay reviewable as Kubernetes manifests without exposing plaintext.
- Age keys are simple to manage locally and in Flux.
- The repo already has `.sops.yaml` path rules for `secret.yaml` and `grafana-env.yaml`.

## Consequences

- Secret files must use names matched by `.sops.yaml`; use `secret.yaml` for app secrets.
- Do not stage plaintext secret files.
- Each environment should have its own Age keypair and matching Flux `sops-age` Secret.

## Operational Notes

- Local Age key path: `~/.config/sops/age/keys.agekey`.
- Encrypt with `sops -i -e kubernetes/apps/<app>/secret.yaml`.
- Verify with `sops -d kubernetes/apps/<app>/secret.yaml` before staging.
- Flux decryption is configured on the cluster-layer apps Kustomization.
