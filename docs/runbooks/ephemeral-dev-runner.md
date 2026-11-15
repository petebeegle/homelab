---
status: draft
scope:
  - development-cluster
  - github-actions
authority: operational
created: 2026-11-06
---

# Disposable development browser runner

## Trust model

One fresh disposable VM per job on a development-only network segment. Do **not** run this on the Talos control-plane, a production Proxmox host namespace, or a long-lived shared CI VM. GitHub's `--ephemeral` registration handles runner scheduling, **not** OS isolation; the VM must be destroyed after each job. No privileged Docker socket, sudo rights, production kubeconfig, 1Password credentials, or production VLAN reachability. Restrict egress to GitHub Actions endpoints, package downloads needed by the browser test, and private development DNS/HTTPS; block production network routes at the hypervisor/firewall. Do not enable this runner for untrusted fork PR code.

## Provisioning (operator prerequisites)

1. Provision a clean Ubuntu x86_64 VM from a trusted immutable image on the development network. Enforce the network ACL above; validate DNS resolves `whoami-<slug>.dev.lab.petebeegle.com` to the development Gateway and HTTPS certificate is trusted. Use a one-job VM lifecycle; shut down and destroy on completion/failure/timeout.
2. Verify and pin a release of `actions/runner` from GitHub, and obtain its official SHA256 checksum. As root, set `RUNNER_VERSION`, `RUNNER_SHA256`, `RUNNER_HOME` and run `tools/development/runner/prepare-vm.sh` from a trusted checkout. The script rejects a mismatched archive.
3. Install browser dependencies in the base VM image (`prepare-vm.sh` installs Chromium's OS libraries using Playwright's pinned dependency list; the workflow installs only the Chromium binaries, unprivileged, and never uses `--with-deps`). Use a trusted, up-to-date image.
4. Obtain a short-lived **repository runner registration token** using a GitHub App or operator-scoped API authorization. Never commit it or print it. Deliver it securely to the VM process as `GITHUB_RUNNER_TOKEN`; it is not the GitHub PAT. Set `RUNNER_HOME=/opt/homelab-actions-runner` and a unique `RUNNER_NAME`. Run `tools/development/runner/run-once.sh` as the unprivileged `runner` user from the VM's trusted local image. Runner registers labels `self-hosted,linux,x64,homelab-dev-browser`, accepts one job, and exits.
5. Destroy the VM after job exit regardless of outcome. Do not restart a used VM or reuse its workspace. The runner is not operational until this provisioning/teardown is automated and demonstrated.

## Workflow and verification

The `Whoami development browser smoke` workflow in PR #447 targets `[self-hosted, linux, x64, homelab-dev-browser]` and runs only via manual `workflow_dispatch`. Dispatch on a trusted ref with an existing Whoami branch slug; it does not deploy anything. Examine GitHub Actions result and uploaded JUnit/Playwright traces. A queued job means no eligible runner was available, **not** a pass.

## Current implementation boundary

`run-once.sh` and `prepare-vm.sh` implement runner registration, pinned binary bootstrap, browser OS libraries and single-job execution inside a guest. `lifecycle.py` implements the Proxmox side: clone, start, registration token, one job, teardown and registration cleanup. It is verified only against a mocked `qm`/ssh, **never against a live Proxmox host**. Nothing in this repository applies firewall or ACL rules, builds the template image, or sweeps for leaked VMs after a hard kill. Until those are done and demonstrated, this is not an operational autonomous runner.

## Management orchestration

From a trusted management machine with pinned SSH host keys, set `GITHUB_RUNNER_ADMIN_TOKEN` using a scoped secret manager and invoke:

```sh
python3 tools/development/runner/lifecycle.py \
  --proxmox-ssh pve04 \
  --template-vmid 900 \
  --vmid 901 \
  --name dev-runner-901 \
  --guest-ssh runner@dev-runner-901
```

These VM IDs and guest hostname are **examples**, not discovered homelab resources. A hardened template must exist, built with `prepare-vm.sh` (which installs the runner, Chromium OS libraries and `/opt/homelab-runner/run-once.sh`), DNS/SSH ready, and firewall isolation. This orchestrator obtains a short-lived GitHub registration token, runs one job under an overall `--deadline` (default 1800s, teardown included), and always attempts teardown: SIGTERM/SIGINT and ordinary failures stop and destroy the VM and remove its runner registration. It refuses to clone onto an existing VMID, and destroys a VM only after `qm config` shows this run's `ephemeral-runner-<id>` description and the expected name. **A hard kill (SIGKILL), OOM, or loss of the management host still leaks the VM**; an independent scheduled sweeper is required and does not exist yet. It cannot run without network/SSH access and a scoped GitHub credential. The orchestrator must not run on the GitHub-hosted runner or in a PR job. CI runs mocked tests for: existing VMID, partial clone, stop/destroy failure, replaced VM, deadline expiry, token never in argv, and ssh option hardening. They do not prove live Proxmox execution, real ssh host-key behavior, or process-death cleanup.
