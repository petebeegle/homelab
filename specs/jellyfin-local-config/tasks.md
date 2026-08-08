---
description: "Jellyfin local config migration task list"
---

# Tasks: jellyfin-local-config

**Input**: `specs/jellyfin-local-config/spec.md` and
`specs/jellyfin-local-config/plan.md`
**Risk Tier**: medium
**Prerequisites**: Branch `codex/jellyfin-local-config` and matching SDD
artifacts.

## Human Gate Status

**Spec Gate**: Approved by Pete after artifact review and authentication/memory
clarification.

**Plan Gate**: Approved by Pete's instruction to open the PR.

**Analyze Requirement**: Completed before implementation; all FRs map to a
manifest, script, test, documentation, or acceptance task, with no unresolved
critical conflict.

## Phase 1: Setup

- [x] T001 [FR-015] Confirm `AGENTS.md`, SDD workflow, storage ADR, SSO runbook,
      chart `3.2.0`, and local-path provisioner behavior.
- [x] T002 [FR-012] Confirm the Authentik blueprint and encrypted Jellyfin secret
      are outside the implementation edit set.

## Phase 2: Implementation

- [x] T003 [FR-001,FR-003] Add `jellyfin-config-local-v1` while retaining
      `jellyfin-config-v2` in `kubernetes/apps/jellyfin/pvc.yaml`.
- [x] T004 [FR-005..FR-011] Add
      `kubernetes/apps/jellyfin/migrate-config.sh`.
- [x] T005 [FR-004,FR-005,FR-013] Update
      `kubernetes/apps/jellyfin/values.yaml` with `Recreate`, ordered
      resource-bounded init containers, and migration volumes.
- [x] T006 [FR-005] Update
      `kubernetes/apps/jellyfin/kustomization.yaml` to generate the migration
      ConfigMap.
- [x] T007 [FR-014] Add the local-path dependency in
      `kubernetes/clusters/production/apps/jellyfin.yaml`.
- [x] T008 [FR-006..FR-011] Add
      `tools/development/tests/test_jellyfin_config_migration.py`, including
      completed-target authentication-loss validation.
- [x] T009 [FR-015] Add
      `docs/decisions/jellyfin-local-config-storage.md`.
- [x] T010 [FR-012,FR-016] Update
      `docs/runbooks/jellyfin-authentik-sso.md`.
- [x] T011 [FR-SETUP] Re-check constitution gates after implementation edits.

## Phase 3: Verification

- [x] T012 [FR-ANALYZE] Complete requirements-to-task analysis before
      implementation.
- [x] T013 [FR-TEST] Run the exact migration script and unit test in an isolated
      local reconstruction.
- [x] T014 [FR-TEST] Parse the proposed Kubernetes YAML with PyYAML.
- [x] T015 [FR-TEST] Run repository pre-commit, k8svalidate, kustomize render,
      decision metadata, architecture, and SDD harness checks.
- [x] T016 [FR-SMOKE] Run both development layers: the exact migration script
      against NFS and `local-path` PVCs passed; the routed Jellyfin branch
      profile was attempted and its GPU-pinning infrastructure exception was
      recorded.
- [ ] T017 [FR-SMOKE] Confirm production preflight: old PVC bound, selected iGPU
      worker `MemoryPressure=False`, safe Proxmox headroom, and native admin
      credential available.
- [ ] T018 [FR-SMOKE] After controlled cutover, verify existing user SSO,
      administrator mapping, native admin login, callback URI, and retained NFS
      PVC.
- [x] T019 [FR-CONVERGE] Reconcile implementation artifacts with discoveries:
      node affinity, stale rollback source, and non-representative branch OIDC
      fixture are recorded.
- [x] T020 [FR-EVIDENCE] Record completed checks and pending production gates
      in `specs/jellyfin-local-config/evidence.md`.

## Phase 4: Commit And PR

- [x] T021 [FR-PR] Commit on `codex/jellyfin-local-config` with a conventional
      commit message.
- [x] T022 [FR-PR] Open draft PR #380 and leave it draft until T015-T018 are
      completed or explicitly reviewed as pending.
- [x] T023 [FR-PR] Commit and push the audit fixes and current evidence to PR
      #380; report the final GitHub Actions result in the PR handoff.
