#!/usr/bin/env python3
"""Provision, start, and always tear down a one-job Proxmox Actions runner VM.

Run from a trusted management machine with SSH access to a dedicated Proxmox host.
The template must already contain the unprivileged runner, dependencies and
tools/development/runner/run-once.sh. No registration token is persisted to disk.
"""
from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request
import json

REPO = "petebeegle/homelab"
VM_NAME = re.compile(r"^[a-z0-9][a-z0-9-]{0,50}$")


def run(argv, *, input=None, check=True):
    return subprocess.run(argv, input=input, text=True, check=check, timeout=3600)


def ssh(host, command, *, input=None):
    return run(["ssh", "-o", "BatchMode=yes", "-o", "StrictHostKeyChecking=yes", host, command], input=input)


def registration_token(github_token):
    request = urllib.request.Request(
        f"https://api.github.com/repos/{REPO}/actions/runners/registration-token",
        data=b"{}",
        method="POST",
        headers={
            "Authorization": f"Bearer {github_token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "homelab-dev-runner",
        },
    )
    with urllib.request.urlopen(request, timeout=20) as response:
        token = json.load(response)["token"]
    if not token:
        raise RuntimeError("GitHub returned an empty registration token")
    return token


def lifecycle(host, template, vmid, name, guest, token):
    if not VM_NAME.fullmatch(name):
        raise ValueError("Invalid runner name")
    if not (100 <= vmid <= 999999) or template == vmid:
        raise ValueError("Invalid VM ID or template")
    created = False
    try:
        # qm commands run only on a dedicated trusted Proxmox management host.
        # Template is a pre-hardened VM with dev-only network and SSH keys.
        ssh(host, f"qm clone {template} {vmid} --name {name} --full 1")
        created = True
        ssh(host, f"qm start {vmid}")
        # Guest SSH requires host-key pinning in the management machine's known_hosts.
        # The runner token is piped via stdin, not placed in argv or Proxmox metadata.
        script = (
            "set -euo pipefail; "
            "IFS= read -r GITHUB_RUNNER_TOKEN; export GITHUB_RUNNER_TOKEN; "
            f"export RUNNER_HOME=/opt/homelab-actions-runner RUNNER_NAME={name}; "
            "exec bash /opt/homelab-runner/run-once.sh"
        )
        for attempt in range(30):
            try:
                ssh(guest, "true")
                break
            except subprocess.CalledProcessError:
                pass
            time.sleep(5)
        else:
            raise RuntimeError("Guest SSH never became ready")
        ssh(guest, "bash -c " + "'" + script.replace("'", "'\\''") + "'", input=token + "\n")
    finally:
        if created:
            # Attempt stop and deletion even if registration or browser job fails.
            try:
                ssh(host, f"qm stop {vmid}", input=None)
            finally:
                ssh(host, f"qm destroy {vmid} --purge 1 --destroy-unreferenced-disks 1")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--proxmox-ssh", required=True, help="Pinned SSH host alias for Proxmox")
    parser.add_argument("--template-vmid", type=int, required=True)
    parser.add_argument("--vmid", type=int, required=True)
    parser.add_argument("--name", required=True)
    parser.add_argument("--guest-ssh", required=True, help="Pinned SSH host alias for VM")
    args = parser.parse_args(argv)
    token = os.environ.get("GITHUB_RUNNER_ADMIN_TOKEN")
    if not token:
        parser.error("GITHUB_RUNNER_ADMIN_TOKEN must be supplied via secret manager")
    lifecycle(args.proxmox_ssh, args.template_vmid, args.vmid, args.name, args.guest_ssh, registration_token(token))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
