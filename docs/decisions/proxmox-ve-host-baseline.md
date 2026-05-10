---
id: ADR-0011
status: accepted
scope:
  - proxmox
  - operations
  - host-baseline
authority: binding
created: 2026-05-10
last_verified: 2026-05-10
supersedes: []
superseded_by:
---

# Proxmox VE Host Baseline

## Decision

The current Proxmox host baseline is Proxmox VE 9 on Debian Trixie.

Host package repository examples and rebuild runbooks should target this baseline unless this decision is superseded.

The Proxmox VE no-subscription repository is acceptable for this homelab because the hosts do not have enterprise subscriptions. Proxmox still recommends the enterprise repository for production support and stability.

## Rationale

- Recording the Proxmox version baseline keeps host rebuild procedures from depending on memory.
- Proxmox VE 9 uses Debian Trixie and the deb822 `.sources` repository format.
- The homelab needs repeatable package repository configuration for recreated Proxmox nodes without requiring an enterprise subscription.

## Consequences

- Proxmox host runbooks should verify the host is Proxmox VE 9 on Debian Trixie before applying version-specific package repository instructions.
- Upgrade or rebuild documentation must be reviewed when the Proxmox host baseline changes.
- The no-subscription repository should be treated as a homelab/non-enterprise choice, not as a general production recommendation.

## Operational Notes

- Check the Proxmox version with `pveversion`.
- Check the Debian suite with `. /etc/os-release && echo "$VERSION_CODENAME"`.
- Configure the Proxmox VE 9 no-subscription repository with `docs/runbooks/proxmox-no-subscription-repository.md`.
