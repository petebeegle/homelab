---
id: ADR-0009
status: accepted
scope:
  - terraform
  - secrets
authority: binding
created: 2026-05-10
last_verified: 2026-05-10
supersedes: []
superseded_by:
---

# Terraform Sensitive Values

## Decision

Sensitive Terraform input values are stored in local untracked `*.tfvars` files. They are not committed to Git and are not SOPS-encrypted in this repo.

Committed Kubernetes Secret manifests continue to use SOPS with Age recipients. Terraform operator credentials and local provider inputs, including Synology provider credentials, are supplied through ignored tfvars files on the operator workstation.

## Rationale

- Terraform provider credentials are local operator inputs rather than Kubernetes desired state.
- Keeping tfvars files untracked avoids committing plaintext or encrypted workstation-specific credentials.
- The repo already ignores `*.tfvars`, which keeps local Terraform inputs out of normal Git review.

## Consequences

- Operators must create or update local tfvars files before running Terraform plans or applies that require sensitive inputs.
- Do not commit tfvars files, encrypted or plaintext.
- Do not use Kubernetes SOPS secret manifests for Terraform provider credentials unless a future decision changes this policy.

## Operational Notes

- Use `terraform.tfvars` or another ignored `*.tfvars` file in the relevant Terraform root.
- Kubernetes Secret files still follow the SOPS policy in `docs/decisions/sops-age-secrets.md`.
