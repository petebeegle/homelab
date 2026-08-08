# Evidence: jellyfin-local-config

**Branch**: `codex/jellyfin-local-config`
**Risk Tier**: medium
**Started**: 2026-08-08

## Spec Kit And Workflow

- Repository-local Spec Kit artifacts and workflow guidance were reused; no
  scaffolding or integration change was required.
- Integration: `codex`.
- The preferred `/workspaces/homelab-worktrees/jellyfin-local-config` path was
  not writable. Work continued in the allowed fallback
  `/home/vscode/homelab-worktrees/jellyfin-local-config`.
- The main checkout's unrelated modified
  `.devcontainer/devcontainer-lock.json` was not touched.
- `.specify/feature.json` points at another active implementation in the shared
  checkout. Prerequisite resolution used the explicit
  `SPECIFY_FEATURE_DIRECTORY=specs/jellyfin-local-config` override; the tracked
  selector file was restored unchanged.
- The PR branch was merged with current `origin/main` before validation.

## Human Gates

| Gate | Result | Notes |
| ---- | ------ | ----- |
| Intent brief | PASS | User requested an engineering audit, fixes, and development validation for draft PR #380. |
| Spec approval | PASS | Existing approved spec preserves authentication and bounds the storage migration. |
| Clarify | PASS | The prior conversation resolved authentication, rollback, node affinity, and memory constraints. |
| Plan approval | PASS | Existing plan was approved when the draft PR was opened; this audit corrects its validation assumptions. |
| Checklist | PARTIAL | Requirements are 21/21 complete. Authentication desired-state and migration-integrity checks are complete; seven live cutover checks remain intentionally open. |
| Tasks/analyze approval | PASS | The user explicitly requested execution of the existing PR and development test work. |
| Converge | PASS | Plan, tasks, tests, generated architecture, and evidence now distinguish migration validation, routed app smoke, and production-only acceptance. |

## Audit Findings And Fixes

1. GitHub Actions run `31278257350` failed only in `Pre-commit`; the architecture
   hook reported that `docs/architecture.md` omitted Jellyfin's new
   `local-path-provisioner` dependency and local PVC. The generated document was
   regenerated.
2. The draft evidence pinned obsolete commit
   `9a8ccf75133aad2013fcaa82383ed4de69d13d56`, causing the SDD harness to reject
   every later commit. The obsolete self-referential final-HEAD claim was
   removed; exact tested SHAs are recorded only for smoke runs.
3. The proposed existing Jellyfin branch profile still uses a fresh
   `nfs-csi-storage` config PVC. A pass cannot prove the production NFS-to-local
   migration. Development validation was split into an exact-script migration
   Job and the routed app profile.
4. Current `main` includes the `immich` smoke profile, while the verifier's
   profile-discovery unit test still expected four apps. The one-line inherited
   expectation was corrected to include `immich` so the current suite passes.
5. The migration suite lacked a restart case for lost critical authentication
   state. A fourth test now proves that an already-marked target fails closed if
   `SSO-Auth.xml` disappears.

## Local Checks

| Command | Result | Notes |
| ------- | ------ | ----- |
| `python3 -m unittest tools/development/tests/test_jellyfin_config_migration.py` | PASS | 4 tests cover complete copy/integrity, completed restart without stale-source comparison, completed-target authentication loss, and missing-source SSO fail-closed behavior. |
| `python3 -m unittest tools/development/tests/test_verify_branch_deploy.py` | PASS | 32 tests passed after correcting the inherited `immich` profile expectation. |
| `python3 -m unittest discover -s tools/codex-harness/tests` | PASS | 73 tests passed. |
| `kubectl kustomize kubernetes/apps/jellyfin` | PASS | Rendered 664 lines before later evidence-only edits. |
| `helm template jellyfin jellyfin/jellyfin --version 3.2.0 -f kubernetes/apps/jellyfin/values.yaml` | PASS | Rendered `Recreate`, ordered `migrate-config` then `install-sso-auth`, target claim `jellyfin-config-local-v1`, and read-only source claim `jellyfin-config-v2`. |
| Production and development cluster renders plus kubeconform `0.7.0` | PASS | 119 resources; 44 valid, 0 invalid, 0 errors, 75 skipped for unavailable schemas. |
| `python3 tools/policy/check_decision_metadata.py` | PASS | ADR metadata accepted. |
| `python3 tools/architecture/render.py --check` | PASS after regeneration | Initial failure reproduced CI and required the generated-document update. |
| `pre-commit run --all-files` | PASS | All configured hooks pass after regeneration. |
| `python3 tools/codex-harness/validate_sdd_context.py ... --require-plan-artifacts --require-evidence` | PASS | Matching branch and complete SDD artifacts accepted after stale SHA removal. |

## Development Validation

### Exact Migration Job

- Timestamp: `2026-08-08T22:13:00Z` (UTC).
- Kubeconfig: `/home/vscode/.kube/homelab-development.config`.
- Namespace: `jellyfin-migration-pr380` (ephemeral).
- Script blob: `07acf46c970cc1b5d54eff0e28169199b1b74474` from
  `kubernetes/apps/jellyfin/migrate-config.sh`.
- Source PVC: `config-source`, `nfs-csi-storage`, `Bound`.
- Target PVC: `config-target`, `local-path`, `Bound` on
  `k8s-premium-martin`.
- Workload: Alpine `3.22` with the production migration command, read-only source
  mount, writable target, and production request/limit bounds.
- Result: PASS. `seed-source=0`, `migrate-config=0`, `verify=0`; marker,
  databases, hidden state, and authentication files copied and byte-matched.
- Cleanup: PASS. The namespace was deleted, both exact test PV reclaim policies
  were changed to `Delete`, and PVs
  `pvc-e647dd86-81d1-47f5-b941-80cd96defdcf` and
  `pvc-da6669cf-8edd-404b-a4e9-7dbf90c0df23` were confirmed deleted.

### Routed Jellyfin Branch Profile

- Profile: `jellyfin`.
- Branch slug: `jellyfin-local-config`.
- Command:
  `python3 tools/development/verify_branch_deploy.py --app jellyfin --branch codex/jellyfin-local-config --slug jellyfin-local-config --push --timeout 20m`.
- Tested HEAD: `3122efc3304db0414c7f4784507c205d2e4053b9`.
- Initial attempt: PRECHECK BLOCKED because the isolated worktree did not contain
  ignored `terraform/development/terraform.tfvars`. The repository staging
  script installed it without logging contents, and the same command was rerun.
- Rerun result: DEVELOPMENT INFRASTRUCTURE EXCEPTION. Flux fetched the exact
  tested SHA; the branch PVC bound, and the Deployment, Service, and HTTPRoute
  rendered. The pod remained Pending because the only development node has
  neither `homelab.petebeegle.com/jellyfin-igpu=true` nor allocatable
  `gpu.intel.com/i915`. No Jellyfin container started, so workload readiness and
  the web-shell response were not verified.
- Resolution: intentionally deferred. Applying Terraform would create the
  missing Proxmox mapping and development VM state and is outside this PR's
  authorized scope; the user confirmed the GPU-pinning limitation should not be
  resolved here.
- Cleanup: PASS after interrupting the wait. The branch Kustomization,
  namespace, GitRepository, PVC, and retained test PV
  `pvc-366dd362-3891-4ca7-a450-e3ba1c5a48da` were confirmed deleted.
- Deliberate limitation: the branch fixture uses a fresh NFS config PVC and a
  placeholder OAuth secret. It is app-regression evidence, not migration or
  production-equivalent OIDC evidence.

## Read-Only Production Preflight

- `jellyfin-config-v2` is `Bound`, `5Gi`, `RWO`, and
  `nfs-csi-storage`.
- Both iGPU workers were `Ready` with `MemoryPressure=False` at inspection time.
  This does not replace the time-sensitive cutover check.
- The running source config was approximately `794376 KiB`, below the proposed
  `10Gi` target size.
- The source contains non-empty `system.xml`, `branding.xml`, `SSO-Auth.xml`, all
  four pinned SSO plugin files, and non-empty `data/jellyfin.db`. Only paths and
  byte sizes were read; no secret contents were printed.
- Safe Proxmox host headroom and possession of a working native administrator
  credential remain unverified and release-blocking.

## Production Acceptance Still Required

- Confirm the selected iGPU worker still has `MemoryPressure=False` and its
  Proxmox host has safe headroom immediately before cutover.
- Confirm `/sso/OID/start/authentik` redirects with the exact HTTPS callback.
- Confirm an existing `Jellyfin Users` member reaches the same account.
- Confirm an existing `Jellyfin Admins` member retains administrator access.
- Confirm a known native local administrator can sign in.
- Confirm the retained NFS PVC remains available after cutover.

These are intentionally not inferred from unit tests, PVC binding, pod
readiness, route status, or the development placeholder identity provider.

## Documentation Impact

- Added binding ADR `docs/decisions/jellyfin-local-config-storage.md`.
- Updated `docs/runbooks/jellyfin-authentik-sso.md`.
- Regenerated `docs/architecture.md`; it was not edited by hand.
- No Spec Kit behavior or standards changed, so an upstream conformance audit is
  not required.

## Final State

- Branch: `codex/jellyfin-local-config`.
- Draft PR: `#380` (`https://github.com/petebeegle/homelab/pull/380`).
- Audit-fix commit tested in development:
  `3122efc3304db0414c7f4784507c205d2e4053b9`.
- Final evidence commit and GitHub Actions result: pending publication/handoff.
- Production authentication acceptance: pending and release-blocking.
