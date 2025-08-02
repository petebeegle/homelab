# GitHub Copilot Custom Instructions for Terraform

applyTo:
  - terraform/**
  - terraform/**/*

## What does this part of the repository do?
This directory manages infrastructure as code for the homelab using Terraform modules, Talos for Kubernetes node provisioning, and Proxmox for VM management. It implements secure, modular, and declarative infrastructure following GitOps and automation best practices.

## What coding style, best practices, or architectural patterns should GitHub Copilot follow?
- Use modules for all infrastructure components; avoid monolithic root modules.
- Use Talos for Kubernetes node provisioning and Proxmox for VM management.
- All variables must be defined in `variables.tf` and documented in `README.md`.
- Use secure defaults and SOPS for secrets/credentials.
- Ensure all resources are idempotent and declarative.
- Follow naming conventions and keep resources minimal and composable.
- Reference `/terraform/cluster/` for cluster infra and `/terraform/environment/` for environment-specific resources.

## What should GitHub Copilot avoid?
- Avoid monolithic or overly complex modules and scripts.
- Avoid hardcoding secrets or sensitive data.
- Avoid non-declarative or imperative configuration unless explicitly required.
- Avoid ignoring project conventions or structure.

## Additional context
- All code and configuration should be production-grade, secure, and maintainable.
- When in doubt, explain your reasoning and reference relevant project conventions.

_Last updated: 2025-08-02_
