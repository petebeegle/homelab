#!/usr/bin/env bash
# Run inside a freshly provisioned, disposable Linux x64 VM on the development network.
set -euo pipefail
umask 077

: "${GITHUB_RUNNER_TOKEN:?Provide a short-lived GitHub runner registration token via stdin wrapper or secret manager}"
: "${RUNNER_HOME:?Set RUNNER_HOME to the unpacked GitHub Actions runner directory}"
: "${RUNNER_NAME:?Set RUNNER_NAME to a unique name for this VM}"

REPO="petebeegle/homelab"
cd "$RUNNER_HOME"
test -x ./config.sh && test -x ./run.sh || { echo "Missing GitHub runner binaries" >&2; exit 1; }

# Register one job only. --ephemeral ensures the GitHub service unregisters it after a job.
# The VM itself MUST be destroyed after exit; ephemeral registration alone does not isolate jobs.
./config.sh --url "https://github.com/$REPO" \
  --token "$GITHUB_RUNNER_TOKEN" \
  --name "$RUNNER_NAME" \
  --labels homelab-dev-browser \
  --ephemeral --unattended --disableupdate --replace
unset GITHUB_RUNNER_TOKEN

# Limit to one job and propagate failure. No automatic restart: rebuild the VM for another job.
exec ./run.sh --once
