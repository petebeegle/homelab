# Dev PR smoke — design specification

Status: **proposal for human decision.** Nothing here is built or applied. Observed facts are separated from proposals.

## Intent
Make "deploy this PR's branch to the development cluster and verify it, including in a real browser" a check that runs on pull requests, without handing PR-controlled code the development kubeconfig or any production reach.

## Observed (from the repository at `origin/main` bdb1802; sources in evidence.md)
- Dev and production share one bridge and subnet: `vmbr0`, `192.168.30.0/24`, gateway `192.168.30.1`. The dev cluster is one VM (VMID 170, `pve04`, `192.168.30.170`); its gateway is `192.168.30.225`. Production nodes and the NAS (`192.168.30.99`) are on the same subnet.
- No firewall, VLAN or ACL is managed as code. There is no Ubuntu/cloud-init template, packer config, GitHub App, or runner controller in the repo.
- Terraform credentials live in untracked tfvars (ADR-0009); dev Terraform state is a local file. `talos_version` has no default on `main`.
- Merged runner code (#447/#448/#451): a manual-dispatch workflow targeting a self-hosted label, and `lifecycle.py` which clones a Proxmox template over ssh `qm`, registers a GitHub runner, runs one job, tears down. Mock-tested only.
- `verify_branch_deploy.py --browser` (PR #452) already runs activate, assertions, browser, cleanup from any machine that can reach dev.

## Requirements
- R1. PR-supplied code never runs where the dev kubeconfig, Proxmox credentials or GitHub credentials exist.
- R2. Any machine that executes PR-supplied code (including browser specs) is disposable, and cannot reach production services, Proxmox management, the NAS or other LAN hosts. It may reach the dev gateway, a DNS resolver and what it needs from the internet.
- R3. Same-repository PRs only; never forks.
- R4. The check is reported against the PR head SHA, covers exactly that SHA, and a missing or stale result is never a pass.
- R5. No inbound webhook endpoint is exposed to the internet; private services stay private.
- R6. Credentials are least-privilege and held only on a trusted management host.
- R7. Cleanup survives process death (sweeper), and break glass exists (the main ruleset's admin-via-PR bypass).

## Key design finding: a GitHub runner may not be needed
Both designs need a trusted component that notices a PR and creates a VM (a GitHub runner VM only exists after something creates it, and GitHub cannot reach a private network). Given that component, compare:

| | A. Ephemeral GitHub Actions runner (current #447/#448 direction) | B. Supervisor reports a commit status (proposed) |
| --- | --- | --- |
| Needs | Poller for queued jobs, VM per job, runner registration | Poller for open PRs, VM per run (only if PR-supplied code runs), ssh |
| GitHub credential | Repository **Administration: write** (mints runner tokens; can also change repo settings and rulesets) | `Commit statuses` / `Checks` write + `Pull requests` read |
| Surface | Runner registration tokens, labels, stale registrations, token visible in guest process list during `config.sh` | None of these |
| PR UX | Actions logs in GitHub | Status with a link to the evidence |
| Fit with #449 | Needs the supervisor anyway | Is the supervisor's first job |

Recommendation: **B.** It removes the most powerful credential and the registration lifecycle, and reuses `lifecycle.py`'s VM handling (clone, ownership marker, deadline, teardown). Option A remains valid if Actions-native logs matter more than the smaller credential; the choice is the user's.

## Proposed trust boundaries
- Management host (trusted, always on, not a PR job): holds the dev kubeconfig, Proxmox credential, and GitHub App key. Runs the supervisor and the verifier **from `main`**, passing the PR branch only as `--branch` (Flux fetches the branch; no PR code executes with the kubeconfig).
- Disposable browser VM (untrusted): created per run from a template, firewalled, destroyed after. Receives the URL and the spec; returns a result and artifacts. Holds no credentials.
- Until the VM exists, only the spec from `main` runs, on the trusted host. A PR that changes `tests/browser/` or the verifier gets no automatic result (status "needs manual run") rather than running unreviewed code on the trusted host.
- Network isolation without a VLAN: Proxmox per-VM firewall on the VM's interface (it filters same-subnet traffic): default-deny egress; allow DNS to the chosen resolver, TCP 443 to the dev gateway `192.168.30.225`, and 80/443 to non-RFC1918 addresses; deny all other RFC1918, which covers production, the NAS and Proxmox management. Managed with the existing bpg/proxmox provider if its firewall resources fit (**unverified**; check provider docs in the implementation spec).

## Non-goals
Production deployments from CI, forks, replacing the Spec Kit workflow, local-model/hosted-model work (#449 phases 3-5), VLAN or UniFi changes.
