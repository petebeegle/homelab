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
# The workflow installs only the Chromium binaries as the unprivileged runner.
# Use Playwright's own dependency list, pinned to the version in tests/browser/package.json,
# so the library set cannot drift from the browser version the tests use. Verified need:
# without these, Chromium fails to start with ~21 missing shared libraries.
repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
playwright_version="$(node -p "require('${repo_root}/tests/browser/package.json').devDependencies['@playwright/test']")"
[[ "$playwright_version" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]] || { echo "Unpinned Playwright version: $playwright_version" >&2; exit 1; }
npx --yes "playwright@${playwright_version}" install-deps chromium
# lifecycle.py runs this exact path in the guest. Root-owned so the runner user cannot alter it.
install -d -m 0755 /opt/homelab-runner
install -m 0755 -o root -g root "$(dirname "${BASH_SOURCE[0]}")/run-once.sh" /opt/homelab-runner/run-once.sh
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
echo "Runner binaries, browser system libraries and /opt/homelab-runner/run-once.sh are in place."
