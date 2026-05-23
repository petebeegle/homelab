---
status: current
scope:
  - foundryvtt
  - blue-green-upgrades
  - nfs-csi-snapshots
created: 2026-05-16
last_verified: 2026-05-16
---

# Foundry Safe Blue/Green Upgrade

Use this runbook for Foundry VTT image upgrades. Production changes stay GitOps-first: the tool edits repository desired state and the operator commits, opens a PR, merges it, and waits for Flux. Do not patch production routes live.

## Safety Model

- Development rehearsal is mandatory before production `prepare`, `promote`, `rollback`, or `retire`.
- `dev-rehearse` uses the small development-only fixture in `kubernetes/apps/foundry-bluegreen-fixture`, not real Foundry and not Foundry secrets.
- `dev-rehearse` only accepts the development kubeconfig at `~/.kube/homelab-development.config` after path expansion and resolution.
- Rehearsal evidence is written to `.codex/tmp/foundry-bluegreen-dev-rehearse.json` and is valid only for the current tool/config version.
- `prepare` pauses the blue Foundry deployment before creating the NFS CSI snapshot desired state.
- `Service/foundryvtt` remains the stable production backend for the existing public and internal routes.
- The original blue `Deployment/foundryvtt` selector intentionally stays app-only for Kubernetes selector immutability and compatibility with the existing live Deployment. Color labels live on pod templates and Services so switching can move traffic without mutating the blue Deployment selector.
- Green preview traffic uses the internal Gateway only at `foundry-green.${cluster_domain}`.
- The development fixture preview is LAN-only at `foundry-green-preview.dev.lab.petebeegle.com`.
- After `promote`, inactive blue remains scaled to zero until an explicit `retire`.

## Development Rehearsal

From a clean implementation branch:

```bash
python3 tools/foundry_bluegreen.py status
python3 tools/foundry_bluegreen.py dev-rehearse
```

The rehearsal applies the safe fixture to development, waits for blue and green HTTP workloads, scales blue to zero, creates `VolumeSnapshot/foundry-fixture-blue-rehearsal` with `VolumeSnapshotClass/nfs-csi-snapshot`, waits for readiness, and scales blue back to one replica.

If development access is unavailable, do not run production commands. Record the blocker in the PR summary and rerun rehearsal when access returns.

## Prepare Green

```bash
python3 tools/foundry_bluegreen.py prepare --image felddy/foundryvtt:<tag>
```

`prepare` fails unless current rehearsal evidence exists. On success it edits `kubernetes/apps/foundryvtt` to:

- scale blue `Deployment/foundryvtt` to zero for snapshot consistency,
- add `VolumeSnapshot/foundryvtt-blue-pre-upgrade`,
- add green PVC, Deployment, preview Service, and internal preview `HTTPRoute`.

Commit the desired-state changes, open a PR, merge it after review, and wait for Flux to reconcile production.

## Promote, Roll Back, Retire

Promote after the green preview is validated:

```bash
python3 tools/foundry_bluegreen.py promote
```

Rollback if green is not acceptable:

```bash
python3 tools/foundry_bluegreen.py rollback
```

Retire only after the promoted state has soaked and rollback is no longer needed:

```bash
python3 tools/foundry_bluegreen.py retire
```

Each command edits repository desired state only. Commit, PR, merge, and wait for Flux after each production step.
