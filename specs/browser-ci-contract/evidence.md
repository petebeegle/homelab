# Evidence

Status: CI PASSED for head 3234b56 (unit/contract layers only). Live browser smoke via this workflow NOT RUN (no runner exists yet).

The workflow uses workflow_dispatch and does not provision, reconcile, or delete cluster resources. No privileged credentials or PR-controlled scripts run on a self-hosted runner. The development Whoami URL must already exist and be reachable from the dedicated isolated development runner. Runner provisioning has not been verified; the manual job may queue until the required runner label exists. No successful browser execution is claimed.

CI at head 3234b56: all 8 checks passed. https://github.com/petebeegle/homelab/actions/runs/42291209700 and https://github.com/petebeegle/homelab/actions/runs/42291209831. The workflow is manual-dispatch only, so these runs did not execute the browser job.

The browser itself was verified separately, from the devcontainer and not via this workflow: see specs/harness-live-smoke/evidence.md (merged in #450).

OS libraries for Chromium must be preinstalled in the runner image (the job installs only the Chromium binaries, unprivileged); prepare-vm.sh in the runner PRs does this.
