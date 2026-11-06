---
status: implementation-ready
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
3. Install browser dependencies in the base VM image (Chromium dependencies; workflow installs Playwright/Chromium itself). Use a trusted, up-to-date image.
4. Obtain a short-lived **repository runner registration token** using a GitHub App or operator-scoped API authorization. Never commit it or print it. Deliver it securely to the VM process as `GITHUB_RUNNER_TOKEN`; it is not the GitHub PAT. Set `RUNNER_HOME=/opt/homelab-actions-runner` and a unique `RUNNER_NAME`. Run `tools/development/runner/run-once.sh` as the unprivileged `runner` user from the VM's trusted local image. Runner registers labels `self-hosted,linux,x64,homelab-dev-browser`, accepts one job, and exits.
5. Destroy the VM after job exit regardless of outcome. Do not restart a used VM or reuse its workspace. The runner is not operational until this provisioning/teardown is automated and demonstrated.

## Workflow and verification

The `Whoami development browser smoke` workflow in PR #447 targets `[self-hosted, linux, x64, homelab-dev-browser]` and runs only via manual `workflow_dispatch`. Dispatch on a trusted ref with an existing Whoami branch slug; it does not deploy anything. Examine GitHub Actions result and uploaded JUnit/Playwright traces. A queued job means no eligible runner was available, **not** a pass.

## Current implementation boundary

These scripts implement runner registration, pinned binary bootstrap, and single-job execution. They **do not** create a VM, issue a registration token, install network firewall rules, or automatically destroy the VM; those require Proxmox access and a scoped GitHub App credential. Until those pieces are wired, this is a prepared runner implementation, not a running autonomous runner.

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

These VM IDs and guest hostname are **examples**, not discovered homelab resources. A hardened template must exist with the runner installation and `/opt/homelab-runner/run-once.sh`, DNS/SSH ready, and firewall isolation. This orchestrator obtains a short-lived GitHub registration token and destroys the cloned VM in a `finally` block. It cannot run without network/SSH access and a scoped GitHub credential. The orchestrator must not run on the GitHub-hosted runner or in a PR job. CI verifies lifecycle failure cleanup through mocked tests; it does not prove live Proxmox execution.
