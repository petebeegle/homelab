# Tasks

- [x] Rewrite lifecycle.py: deadline, signal-safe teardown, ownership marker, free-VMID check, independent cleanup, registration cleanup, argument hardening.
- [x] Replace tests with a stateful fake Proxmox covering the failure paths.
- [x] Mutation-check that each protection is guarded by a specific failing test (7/7).
- [x] prepare-vm.sh: pinned Playwright OS libraries; install run-once.sh to /opt/homelab-runner/.
- [x] Reconcile runbook and #448 spec records with the code.
- [ ] Live run against a real Proxmox host and template.
- [ ] Scheduled sweeper for VMs leaked by SIGKILL/OOM/host loss.
- [ ] Per-run runner label (requires a #447 workflow change).
- [ ] Per-VM guest ssh host-key pinning (template currently shares one key across clones).
- [ ] Dev-only network ACLs as code; verify production is unreachable.
