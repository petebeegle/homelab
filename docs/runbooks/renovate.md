---
status: current
scope:
  - renovate
  - dependency-management
created: 2026-05-16
last_verified: 2026-05-16
---

# Renovate

Renovate runs in the `renovate` namespace and reads repository policy from
`renovate.json`.

## Flux Updates

Flux component updates found in
`kubernetes/clusters/**/flux-system/gotk-components.yaml` are grouped into a
single `fluxcd` pull request. Generated `gotk-*.yaml` files are ignored by
yamllint at the top-level `.yamllint.yaml` ignore scope; Kubernetes render and
schema validation still run against the cluster kustomizations.

## Terraform Docs

Terraform dependency updates run
`./tools/renovate/update-terraform-docs.sh` as a Renovate post-upgrade task. The
script refreshes Terraform READMEs containing `<!-- BEGIN_TF_DOCS -->` with
pinned `terraform-docs` v0.23.0, matching CI and pre-commit expectations.

The self-hosted Renovate app allows only this exact command for Terraform docs
regeneration. The script uses an existing `terraform-docs` only when it is
v0.23.0; otherwise it downloads the pinned linux-amd64 release into a temporary
directory and removes it before exiting.
