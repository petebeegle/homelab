# Implementation Plan: jellyfin-local-config

**Branch**: `codex/jellyfin-local-config` | **Date**: 2026-08-08 | **Spec**:
`specs/jellyfin-local-config/spec.md`

**Input**: Feature specification from
`specs/jellyfin-local-config/spec.md`

## Summary

Create a new 10 GiB `local-path` config PVC, retain the current NFS PVC, and use
an ordered, resource-bounded migration init container to copy and validate the
complete config before the existing SSO bootstrap runs. Set the Jellyfin
Deployment to `Recreate`, add the local-path Flux dependency, document the
storage exception and authentication cutover contract, and add an executable
migration test.

## Technical Context

**Risk Tier**: medium
**Workflow Tier**: medium
**Primary Areas**: Kubernetes, Flux, storage, Jellyfin, Authentik-adjacent
authentication, tests, runbooks, decision records
**Dependencies**: Flux, Jellyfin Helm chart `3.2.0`, local-path-provisioner,
Synology NFS CSI, Intel GPU device plugin, Python `unittest`, POSIX shell tools
**Storage**: App-specific `local-path` exception for `/config`; Synology NFS
retained for media and migration source
**Ingress**: Existing Cilium Gateway API route unchanged
**Secrets**: Existing SOPS-encrypted `jellyfin-secrets` reference unchanged
**Smoke Strategy**: Focused migration unit tests and manifest render checks; an
ephemeral development Job that runs the exact migration script from an NFS PVC
to a `local-path` PVC; the existing routed Jellyfin branch smoke for application
regression; manual authentication acceptance before promotion
**Fanout Targets**: Read-only manifest/ADR validation and migration unit test can
run independently; all results consolidate in `evidence.md`
**Development Validation**: Use two complementary layers. The existing Jellyfin
profile proves the branch fixture reconciles, starts, routes, and serves its web
shell, but its fresh NFS-backed config does not exercise the production
migration. A one-off isolated development Job therefore runs the exact migration
script against an NFS source PVC and a `local-path` target PVC, verifies copied
database, hidden, and authentication state, and removes all test resources.
If the development node lacks the fixture's required iGPU label/resource, record
that routed-profile infrastructure exception without weakening the production or
branch GPU pinning; do not apply Terraform merely to satisfy this PR's smoke.
**Post-Implementation SDD Conformance**: Local repository sources only; this
change does not alter Spec Kit behavior or standards.

## Human Gates

**Spec Gate**: Approved by Pete after reviewing the proposed spec and explicitly
adding authentication and memory constraints.

**Checklist Status**: Requirements checklist PASS. Authentication desired-state
and migration-integrity sections PASS; seven time-sensitive cutover acceptance
items remain intentionally open until production rollout.

**Plan Gate**: Approved by Pete's "Ok let's open the PR" after the proposed
architecture, authentication safeguards, and memory preflight were presented.

**Expected Task/Analyze Gate**: PASS; requirements were mapped to implementation
and validation tasks before tracked changes. No unresolved requirement conflicts
remain.

## Constitution Check

*GATE: Must pass before tracked edits and be re-checked before commit.*

- [x] GitOps source of truth preserved; no durable live-cluster-only state.
- [x] No production-first mutation; development validation is identified as
      pending in the draft PR rather than falsely reported.
- [x] Gateway API invariant preserved; no new Kubernetes `Ingress` resources.
- [x] SOPS invariant preserved; no plaintext secret manifests staged.
- [x] NFS default considered; the app-specific local storage exception is
      recorded in binding ADR-0015.
- [x] Talos boundary preserved; no SSH-based node operations introduced.
- [x] Branch is `codex/jellyfin-local-config`; tracked edits use the allowed
      `/home/vscode/homelab-worktrees/jellyfin-local-config` fallback because the
      preferred `/workspaces/homelab-worktrees/` path is not writable here.
- [x] Documentation impact identified; SSO runbook and binding ADR are updated.
- [x] PR review/status checks remain the review gate.

## Project Structure

### SDD Artifacts

```text
specs/jellyfin-local-config/
├── checklists/
│   ├── authentication.md
│   └── requirements.md
├── spec.md
├── plan.md
├── tasks.md
└── evidence.md
```

### Source Or Documentation Changes

```text
docs/decisions/jellyfin-local-config-storage.md
docs/runbooks/jellyfin-authentik-sso.md
kubernetes/apps/jellyfin/kustomization.yaml
kubernetes/apps/jellyfin/migrate-config.sh
kubernetes/apps/jellyfin/pvc.yaml
kubernetes/apps/jellyfin/values.yaml
kubernetes/clusters/production/apps/jellyfin.yaml
tools/development/tests/test_jellyfin_config_migration.py
specs/jellyfin-local-config/**
```

## Tiered TDD And Validation Plan

**TDD expectation**: Add a focused `unittest` seam for the standalone migration
script. The tests construct representative Jellyfin/SSO state, exercise the
copy, retry, and fail-closed paths, and run before relying on rendered manifests.

**Local checks**:

- `python3 -m unittest tools/development/tests/test_jellyfin_config_migration.py`
- `pre-commit run yamllint --files kubernetes/apps/jellyfin/pvc.yaml kubernetes/apps/jellyfin/values.yaml kubernetes/apps/jellyfin/kustomization.yaml kubernetes/clusters/production/apps/jellyfin.yaml`
- `pre-commit run k8svalidate --files kubernetes/apps/jellyfin/pvc.yaml kubernetes/apps/jellyfin/kustomization.yaml kubernetes/clusters/production/apps/jellyfin.yaml`
- `kubectl kustomize kubernetes/apps/jellyfin >/tmp/jellyfin-render.yaml`
- `python3 tools/policy/check_decision_metadata.py`
- `python3 tools/architecture/render.py --check`
- `python3 tools/codex-harness/validate_sdd_context.py --root "$(pwd)" --branch "$(git branch --show-current)" --require-plan-artifacts --require-evidence`

**Development smoke**: Run the existing Jellyfin branch verifier, then run an
isolated migration Job using the exact production script, source/target storage
classes, image, mounts, and resource bounds. Confirm both PVCs bind, all
containers exit zero, copied state byte-matches, the routed Jellyfin web shell is
reachable, and cleanup removes the namespace and retained test PVs. A
production-equivalent existing-user OIDC login cannot be represented by the
current branch fixture because it uses a placeholder secret and branch-specific
callback.

**Automated smoke preference**: The routed development profile remains the first
user-path check. Production cutover adds explicit SSO start, existing-user,
administrator, and native-login acceptance.

**Completion evidence**: After merge, record the source fetched SHA, HelmRelease
applied SHA, live Deployment strategy, PVC binding/node, init-container
completion, exact Jellyfin URL result, and authentication outcomes.

**Fanout plan**: Migration test, YAML/render validation, decision metadata
validation, and read-only diff review are independent. Results consolidate in
`specs/jellyfin-local-config/evidence.md`.

**Evidence destination**:
`specs/jellyfin-local-config/evidence.md`.

## Documentation Impact

- Add binding ADR-0015 for the local config exception and availability tradeoff.
- Extend the Jellyfin Authentik SSO runbook with migration preflight,
  authentication acceptance, and rollback.
- Generated `docs/architecture.md` must be checked by
  `tools/architecture/render.py`; it must not be edited manually.

## Implementation Steps

1. Add the local PVC while retaining the NFS source PVC.
2. Add the standalone fail-closed migration script and fixed-name ConfigMap
   generator.
3. Point Jellyfin `/config` at the local PVC, add ordered init containers,
   resource bounds, source/config map volumes, and `Recreate`.
4. Add `local-path-provisioner` to the production Flux dependencies.
5. Add migration unit tests.
6. Add ADR, runbook, SDD artifacts, and checklists.
7. Run the full local check set, the isolated development migration Job, and the
   routed Jellyfin branch smoke; keep production-only authentication acceptance
   pending.
8. Open a draft PR; do not mark it ready until cluster smoke and cutover
   preflight are completed.

## Risks

| Risk | Mitigation |
| ---- | ---------- |
| Existing users or SSO state are lost | Copy the complete tree, byte-compare databases and pinned SSO artifacts, preserve the source PVC, and require live SSO/native acceptance. |
| Jellyfin starts from a partial target | Marker is written only after validation; an unmarked target is cleared and recopied; init failure blocks startup. |
| Concurrent SQLite access corrupts state | Use Deployment `Recreate` and a read-only source mount. |
| Local PVC binds to a pressured node | Require `MemoryPressure=False` and safe Proxmox headroom before accepting cutover. |
| Init copy worsens memory pressure | Keep main request unchanged and bound the copy init container to 64 MiB request/512 MiB limit. |
| Node failure strands local config | Document node affinity, retain NFS rollback source, and keep PR draft until operator accepts the tradeoff. |
| Old NFS rollback state becomes stale | Document that it is immediate rollback only and that later rollback can lose post-cutover changes. |
| Development fixture cannot complete real OIDC login | Keep PR draft, run available routed smoke, and require controlled production existing-user/admin/native acceptance. |

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
| --------- | ---------- | ------------------------------------ |
| App-specific exception to NFS default | SQLite/config latency is the suspected bottleneck | Keeping `/config` on the same NFS class does not address the targeted I/O path. |
| Node-affine local storage | Provides lowest-latency config path using already-installed storage | A new shared block-storage architecture is broader than this bounded Jellyfin change. |
