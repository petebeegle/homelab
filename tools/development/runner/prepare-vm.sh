#!/usr/bin/env bash
# Bootstrap a *new disposable* Ubuntu x86_64 VM, not a shared machine or Kubernetes node.
set -euo pipefail
: "${RUNNER_VERSION:?Set a vetted GitHub Actions runner release version, e.g. 2.x.y}"
: "${RUNNER_SHA256:?Set the official SHA256 checksum for the exact runner tarball}"
: "${RUNNER_HOME:=/opt/homelab-actions-runner}"
test "$(id -u)" -eq 0 || { echo "Run as root on the disposable VM" >&2; exit 1; }
apt-get update
DEBIAN_FRONTEND=noninteractive apt-get install -y ca-certificates curl tar nodejs npm python3 libicu-dev libssl-dev
# Browser OS libraries must be installed as root at image-build time, not in a CI job.
# The workflow installs only Chromium as an unprivileged runner.
install -d -m 0755 "$RUNNER_HOME"
archive="$(mktemp)"
trap 'rm -f "$archive"' EXIT
curl --fail --location --silent --show-error \
  "https://github.com/actions/runner/releases/download/v${RUNNER_VERSION}/actions-runner-linux-x64-${RUNNER_VERSION}.tar.gz" -o "$archive"
echo "${RUNNER_SHA256}  $archive" | sha256sum --check --status
tar -xzf "$archive" -C "$RUNNER_HOME"
# Runner must run unprivileged; never grant sudo or mount Docker/host sockets.
id -u runner >/dev/null 2>&1 || useradd --system --create-home --shell /bin/bash runner
chown -R runner:runner "$RUNNER_HOME"
echo "Runner binaries ready. Install browser system dependencies on this disposable image before starting run-once.sh."
