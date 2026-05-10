# Proxmox No-Subscription Repository

Use this runbook to configure the Proxmox VE no-subscription repository when recreating or creating Proxmox hosts.

This procedure applies to the current Proxmox host baseline: Proxmox VE 9 on Debian Trixie. See `docs/decisions/proxmox-ve-host-baseline.md`.

Proxmox says the no-subscription repository does not require a subscription key and can be used for testing or non-production use. It is not recommended for production servers because packages are not always tested and validated as heavily as the enterprise repository.

Reference: <https://pve.proxmox.com/pve-docs/chapter-sysadmin.html>

## Pre-Checks

Confirm the host is Proxmox VE 9:

```bash
pveversion
```

Confirm the host is running Debian Trixie:

```bash
. /etc/os-release
echo "$VERSION_CODENAME"
```

Expected codename:

```text
trixie
```

Confirm the Proxmox archive keyring exists:

```bash
test -f /usr/share/keyrings/proxmox-archive-keyring.gpg
```

If the keyring is missing, stop and follow the current Proxmox documentation before continuing.

## Configure Repository

Disable the enterprise repository on unsubscribed hosts to avoid apt authentication errors. Check for enterprise source files:

```bash
grep -R "enterprise.proxmox.com" /etc/apt/sources.list /etc/apt/sources.list.d/ || true
```

Comment out or remove the enterprise Proxmox source on hosts without a subscription.

Create or update `/etc/apt/sources.list.d/proxmox.sources`:

```text
Types: deb
URIs: http://download.proxmox.com/debian/pve
Suites: trixie
Components: pve-no-subscription
Signed-By: /usr/share/keyrings/proxmox-archive-keyring.gpg
```

## Verify

Refresh package metadata:

```bash
apt update
```

Expected outcomes:

- Apt reads `http://download.proxmox.com/debian/pve`.
- Apt does not report enterprise repository authentication errors.
- The configured suite is `trixie`.

Treat `apt full-upgrade` as a separate reviewed maintenance action after repository configuration is verified.
