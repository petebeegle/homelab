# Plan: fix-wireguard-endpoint

SDD tier: medium. Workflow risk tier: high.
Smoke strategy: isolated reconciliation against a disposable database; rendered
manifests and secret comparison; development execution if available. Production
mobile handshake and browsing require the external client and remain unverified.
Fanout targets: read-only verifier review alongside local validation and evidence.
All implementation edits remain sequential under one owner.

1. Correct only WG_HOST in the SOPS Secret.
2. Supply WG_EASY_HOST to the existing defaults initContainer from that Secret.
3. Extend its existing parameterized update to reconcile user_configs_table.host.
4. The new initContainer environment reference changes the pod template and
   triggers a restart when Flux applies it. Fresh installs retain normal setup.
5. Test stale-host correction, preservation, idempotency, missing database/row,
   and required host; render and validate encryption.
6. Document rollout and existing-profile limitations and record evidence.

Rollback: revert the commit through GitOps; no database/key reset.
Exceptions: default worktree parent is unwritable, so use
/home/vscode/homelab-worktrees/fix-wireguard-endpoint. Home-level kubeconfig and
Age key are used in place; no repo-relative ignored secrets are needed.
The user's explicit update request is used as combined authorization for the
bounded correction; no broader networking redesign is included.
