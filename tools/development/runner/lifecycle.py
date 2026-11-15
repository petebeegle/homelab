#!/usr/bin/env python3
"""Provision, start, and always tear down a one-job Proxmox Actions runner VM.

Run from a trusted management machine with SSH access to a dedicated Proxmox host.
The template must already contain the unprivileged runner, dependencies and
tools/development/runner/run-once.sh.

Safety properties (all exercised by tests/test_lifecycle.py with mocked ssh):
- one overall deadline bounds every step, including teardown retries;
- SIGTERM/SIGINT run teardown (a hard kill or host loss does NOT; see the runbook);
- the VMID must be free before cloning, and a VM is destroyed only after its
  config shows this run's ownership marker and name;
- cleanup steps are independent and never mask the primary failure;
- the registration token travels over ssh stdin, never in ssh argv or Proxmox
  metadata. It IS briefly visible in the guest's process list while the runner's
  config.sh runs, so the guest must not run untrusted code before registration.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shlex
import signal
import subprocess
import sys
import time
import urllib.error
import urllib.request
import uuid

REPO = "petebeegle/homelab"
VM_NAME = re.compile(r"^[a-z0-9][a-z0-9-]{0,40}$")
SSH_ALIAS = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._@-]{0,100}$")
DEFAULT_DEADLINE = 1800  # seconds for the whole run, teardown included
TEARDOWN_RESERVE = 180  # seconds always kept back for teardown
STEP_TIMEOUT = 120
OWNER_PREFIX = "ephemeral-runner-"


class Deadline:
    def __init__(self, seconds):
        self.end = time.monotonic() + seconds

    def remaining(self):
        return self.end - time.monotonic()


def ssh(host, command, *, input=None, timeout=STEP_TIMEOUT, capture=False):
    """Run one command over ssh. Returns stdout (only when capture=True)."""
    argv = [
        "ssh",
        "-o", "BatchMode=yes",
        "-o", "StrictHostKeyChecking=yes",
        "-o", "ConnectTimeout=10",
        "-o", "ServerAliveInterval=15",
        "-o", "ServerAliveCountMax=3",
        "--", host, command,
    ]
    result = subprocess.run(
        argv, input=input, text=True, check=True, timeout=max(1, int(timeout)),
        stdout=subprocess.PIPE if capture else None,
    )
    return result.stdout if capture else ""


def _ok(host, command, *, timeout=STEP_TIMEOUT):
    try:
        ssh(host, command, timeout=timeout)
        return True
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
        return False


def _github(github_token, method, path, *, data=None):
    request = urllib.request.Request(
        f"https://api.github.com/repos/{REPO}/{path}",
        data=data, method=method,
        headers={
            "Authorization": f"Bearer {github_token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "homelab-dev-runner",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            body = response.read()
    except urllib.error.HTTPError as exc:
        # Report only the status: response bodies and headers can echo request details.
        raise RuntimeError(f"GitHub API {method} {path} failed: HTTP {exc.code}") from None
    except urllib.error.URLError as exc:
        raise RuntimeError(f"GitHub API {method} {path} unreachable: {type(exc.reason).__name__}") from None
    return json.loads(body) if body else {}


def registration_token(github_token):
    token = _github(github_token, "POST", "actions/runners/registration-token", data=b"{}").get("token")
    if not token:
        raise RuntimeError("GitHub returned an empty registration token")
    return token


def delete_registration(github_token, name):
    """Best effort: remove a runner registration left behind if the job never ran."""
    runners = _github(github_token, "GET", "actions/runners?per_page=100").get("runners", [])
    for runner in runners:
        if runner.get("name") == name:
            _github(github_token, "DELETE", f"actions/runners/{int(runner['id'])}")
            return True
    return False


def owned(host, vmid, name, run_id):
    """True only if the VM at vmid carries this run's marker and name."""
    try:
        config = ssh(host, f"qm config {int(vmid)}", capture=True)
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
        return False
    return f"{OWNER_PREFIX}{run_id}" in config and re.search(rf"^name: {re.escape(name)}$", config, re.M) is not None


def teardown(host, vmid, name, runner_name, run_id, github_token):
    """Stop and destroy the VM, then drop its registration. Returns a list of error strings."""
    errors = []
    if _ok(host, f"qm status {int(vmid)}"):  # the VM exists
        if not owned(host, vmid, name, run_id):
            errors.append(f"refusing to destroy VM {vmid}: ownership marker/name mismatch")
        else:
            if not _ok(host, f"qm stop {int(vmid)} --timeout 30", timeout=60):
                errors.append(f"qm stop {vmid} failed (destroy will still be attempted)")
            destroyed = False
            for _ in range(3):
                if _ok(host, f"qm destroy {int(vmid)} --purge 1 --destroy-unreferenced-disks 1 --skiplock 1", timeout=90):
                    destroyed = True
                    break
                time.sleep(2)
            if not destroyed:
                errors.append(f"qm destroy {vmid} failed after retries: VM may be leaked")
    try:
        delete_registration(github_token, runner_name)
    except (RuntimeError, ValueError, KeyError) as exc:
        errors.append(f"registration cleanup failed: {exc}")
    return errors


def lifecycle(host, template, vmid, name, guest, token, *, github_token="", deadline_seconds=DEFAULT_DEADLINE):
    if not VM_NAME.fullmatch(name):
        raise ValueError("Invalid runner name")
    for alias in (host, guest):
        if not SSH_ALIAS.fullmatch(alias):
            raise ValueError("Invalid ssh host alias")
    if not (100 <= vmid <= 999999) or template == vmid:
        raise ValueError("Invalid VM ID or template")

    run_id = uuid.uuid4().hex[:12]
    runner_name = f"{name}-{run_id[:6]}"
    deadline = Deadline(deadline_seconds)

    def budget(cap=STEP_TIMEOUT):
        remaining = deadline.remaining() - TEARDOWN_RESERVE
        if remaining <= 0:
            raise TimeoutError("overall deadline reached before the job finished")
        return min(cap, remaining)

    primary = None
    attempted = False
    try:
        if _ok(host, f"qm status {int(vmid)}"):
            raise RuntimeError(f"VM {vmid} already exists; refusing to reuse or destroy it")
        attempted = True  # from here on teardown may need to remove a partial clone
        ssh(host, f"qm clone {int(template)} {int(vmid)} --name {shlex.quote(name)} "
                  f"--description {OWNER_PREFIX}{run_id} --full 1", timeout=budget(600))
        ssh(host, f"qm start {int(vmid)}", timeout=budget())
        # The token goes over stdin: not in ssh argv, not in Proxmox metadata.
        script = (
            "set -euo pipefail; "
            "IFS= read -r GITHUB_RUNNER_TOKEN; export GITHUB_RUNNER_TOKEN; "
            f"export RUNNER_HOME=/opt/homelab-actions-runner RUNNER_NAME={shlex.quote(runner_name)}; "
            "exec bash /opt/homelab-runner/run-once.sh"
        )
        while True:
            try:
                ssh(guest, "true", timeout=budget(15))
                break
            except subprocess.CalledProcessError:
                budget()  # raises TimeoutError once the deadline is gone
                time.sleep(5)
        ssh(guest, "bash -c " + shlex.quote(script), input=token + "\n", timeout=budget(deadline.remaining()))
    except BaseException as exc:  # noqa: BLE001 - re-raised after teardown
        primary = exc
    finally:
        errors = []
        if attempted:
            # A second SIGTERM must not interrupt teardown.
            previous = signal.signal(signal.SIGTERM, signal.SIG_IGN)
            try:
                errors = teardown(host, vmid, name, runner_name, run_id, github_token)
            finally:
                signal.signal(signal.SIGTERM, previous)
        for line in errors:
            print(f"cleanup: {line}", file=sys.stderr)
    if primary is not None:
        raise primary
    if errors:
        raise RuntimeError("; ".join(errors))


def _terminate(signum, _frame):
    raise SystemExit(128 + signum)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--proxmox-ssh", required=True, help="Pinned SSH host alias for Proxmox")
    parser.add_argument("--template-vmid", type=int, required=True)
    parser.add_argument("--vmid", type=int, required=True)
    parser.add_argument("--name", required=True)
    parser.add_argument("--guest-ssh", required=True, help="Pinned SSH host alias for VM")
    parser.add_argument("--deadline", type=int, default=DEFAULT_DEADLINE, help="Overall seconds, teardown included")
    args = parser.parse_args(argv)
    github_token = os.environ.get("GITHUB_RUNNER_ADMIN_TOKEN")
    if not github_token:
        parser.error("GITHUB_RUNNER_ADMIN_TOKEN must be supplied via secret manager")
    signal.signal(signal.SIGTERM, _terminate)
    try:
        token = registration_token(github_token)
        lifecycle(args.proxmox_ssh, args.template_vmid, args.vmid, args.name, args.guest_ssh, token,
                  github_token=github_token, deadline_seconds=args.deadline)
    except (RuntimeError, ValueError, TimeoutError, subprocess.SubprocessError) as exc:
        # Never print exc.cmd/exc.input: only a sanitized message.
        print(f"runner lifecycle failed: {type(exc).__name__}: {exc if not isinstance(exc, subprocess.SubprocessError) else 'command failed'}",
              file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
