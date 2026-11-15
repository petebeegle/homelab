# Tasks

- [x] Gather repository facts for hosts, network, templates, credentials and existing runner code (read-only).
- [x] Write the proposal with observed/proposed separated, a comparison of the two designs, trust boundaries and staging.
- [ ] User decisions 1-8 in plan.md.
- [ ] Stage 1 implementation spec: `pr-smoke` command and `dev-smoke` commit status (informational).
- [ ] Stage 2 implementation spec: runner infrastructure Terraform root, firewall proof, sweeper.
- [ ] Verify the bpg/proxmox firewall resources against provider documentation before relying on them.
- [ ] Stage 3: always-on poller, GitHub App, alerting, then required check.
