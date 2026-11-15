# Dev PR smoke — plan

SDD tier: low (docs-only proposal). Workflow risk: docs-only. Smoke strategy: none (no runtime change). Fanout: one read-only discovery agent produced the repository facts (evidence.md); design is single-owner. Exceptions: none. Human gate: the user asked for this to be fleshed out ("yeah lets flesh this out"); every infrastructure step below needs its own implementation, spec and approval. Do not treat this document as approval to build.

## Staged path (each stage is independently useful and verified before the next)

**Stage 0 — done.** `verify_branch_deploy.py --browser` (#452): activate, assert, browser, cleanup on demand from a machine that can reach dev. Informational for agents.

**Stage 1 — PR smoke command, informational.** A `tools/supervisor`-style command `pr-smoke <PR#>` run by hand or cron on the trusted host:
1. Resolve the PR; refuse forks and drafts-with-unreviewed-test-changes; take the head SHA and branch.
2. Map changed paths to a smoke profile (`kubernetes/apps/<app>/**` to profile `<app>`). No profile means a `success` status saying "no smoke profile", never silence.
3. Run the verifier from `main` with `--branch <PR branch> --browser`. Skip the Terraform step only when the PR touches no `terraform/**` (record that in the status); a PR that does touch Terraform is "needs manual run".
4. Post a commit status `dev-smoke` on the head SHA (pending, then success/failure) linking to the evidence.
5. Serialize runs (one dev environment at a time) and bind the result to the SHA; a newer push invalidates it.
Acceptance: a real PR gets a correct status; a deliberately broken PR gets `failure`; a force-push invalidates the old result; two PRs queue and do not collide; cleanup always runs. Not a required check yet.

**Stage 2 — isolation.** Needed before any PR-supplied code (specs, verifier changes) executes.
- Terraform root (proposed `terraform/external/dev-runner`): Ubuntu 24.04 cloud image, a template VM, reserved VMID range and a Proxmox pool, and the per-VM firewall described in spec.md. Template built with `prepare-vm.sh`.
- Move the browser step to a disposable VM via `lifecycle.py` (clone, ownership marker, deadline, teardown), with the GitHub registration code made optional if Option B is chosen.
- Prove: from the VM, the dev gateway is reachable and production, the NAS and Proxmox management are not. Force failure, timeout and supervisor kill; prove teardown.
- Scheduled sweeper for VMs leaked by SIGKILL/OOM/host loss.

**Stage 3 — always on and required.** Poller on the management host, a GitHub App with least-privilege permissions, alerting when the supervisor is down (Grafana is already in the stack), then make `dev-smoke` a required check only after a stable period. Until then a missing status must not block merges; the ruleset's admin-via-PR bypass is the escape hatch.

## Decisions needed from the user
1. **A or B?** Supervisor-reported status (recommended) or an ephemeral GitHub Actions runner. Affects the GitHub credential and whether #447's workflow is used.
2. **Which Proxmox host** runs the disposable VMs: `pve04` (beside the dev cluster, VMID 170, 24 GB) or another node with free capacity? Datastore (only `local-lvm` is seen in the repo)?
3. **Template source:** Ubuntu 24.04 cloud image built by Terraform (proposed) or a template you already maintain? A reserved VMID range (proposed 9100-9199) and a Proxmox pool?
4. **Isolation mechanism:** per-VM Proxmox firewall (proposed, no VLAN) or a new VLAN via UniFi (manual, not in IaC)? Which resolver serves `*.dev.lab.petebeegle.com` to LAN clients (not found in the repo)?
5. **Management host:** where does the supervisor run (always-on machine; the devcontainer is not one)? Where do the kubeconfig, Proxmox token and GitHub App key live (1Password with the existing operator pattern, or local tfvars per ADR-0009)?
6. **Proxmox credential:** keep ssh `qm` as root (current `lifecycle.py`) or move to the Proxmox HTTPS API with a token scoped to the pool (proposed; needs a `lifecycle.py` change)?
7. **GitHub credential:** a GitHub App (proposed) or a fine-grained PAT, and the exact permissions for the chosen option.
8. **Terraform in PR checks:** dev state is a local file and `talos_version` has no default. Move state to a remote backend, or keep Terraform out of the PR smoke and treat Terraform PRs as manual?

## Risks
- The check's availability becomes a merge dependency; mitigated by staging (informational first) and the bypass.
- One dev cluster means serialized runs; slow PR queues are possible.
- Branch manifests run in the dev cluster, which shares a LAN with production; that is an existing accepted property of dev-first validation, unchanged here.
- Chromium needs OS libraries and Playwright's installer hung under Node 26 in the devcontainer (specs/harness-live-smoke); the template build must be verified, not assumed.
