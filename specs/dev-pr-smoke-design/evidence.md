# Evidence — dev PR smoke design

Date: 2026-11-15. Docs-only; no code, infrastructure, ruleset or PR was changed by this implementation. State: PROPOSAL.

## Sources

Repository facts came from a read-only discovery agent over `origin/main` (bdb1802): Proxmox nodes `pve01..pve04` and the dev VM on `pve04` (`terraform/development/variables.tf`, `docs/runbooks/development-cluster.md`); shared `vmbr0` / `192.168.30.0/24` for dev and production (same terraform roots); VM creation from a Talos ISO via the `terraform/modules/vm` module with disks on `local-lvm`; absence of any Ubuntu/cloud-init template, packer config, firewall/VLAN IaC, GitHub App or runner controller; credential conventions (ADR-0009 tfvars, SOPS, 1Password operator); the merged runner code and runbook. The lead re-checked the Terraform state and `talos_version` findings directly while running the live verifier (specs/dev-browser-smoke/evidence.md).

## Not verified

- The agent's report was not independently re-read file by file; the load-bearing facts (shared subnet, no template, no firewall IaC, local state, missing default) each have a second source in this session or are called out as the agent's finding.
- bpg/proxmox firewall resource support: unverified.
- GitHub App permission names and whether Option B's status/check API fits a required check on a public repository: unverified against current GitHub documentation.
- Proxmox host capacity, free VMIDs, datastores, and which resolver serves dev DNS to LAN clients: unknown; these need the user or a live inventory.
- Whether per-VM Proxmox firewall rules filter same-subnet traffic as assumed in spec.md: standard behavior on the VM's tap interface, but not tested here.

## Validation

`python3 tools/codex-harness/validate_sdd_context.py --require-plan-artifacts --require-evidence` and `git diff --check`; pre-commit hooks on commit.
